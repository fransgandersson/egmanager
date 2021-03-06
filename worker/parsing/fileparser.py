import logging
from logging import handlers
import os
import re

from parsing.handparser import HandParser, HandParserSingleThread
from hand.hand import PlayerHand
from database.mongo.filelogger import FileLogger
from database.mongo.inserters import hand_inserter, player_inserter, player_hand_inserter, cache_inserter
from database.mongo.cache import Cache


LOG_FILENAME = 'fileparser.log'


class FileParser:

    __new_hand_regex = re.compile("PokerStars Hand #([\w]+): ")

    def __init__(self, folder, file_name, single_thread=False):
        self.parsers = list()
        self.logger = None
        self.single_thread = single_thread
        self.path = os.path.join(folder, file_name)
        self.fileLogger = FileLogger(file_name)
        self.cache = None

    def parse(self):
        # Create error log
        self.__create_log()

        # Start the file log
        # The file log contains the
        # file we are currently parsing
        # It can be implemented e.g. as a database
        # Update its status to 'parsing'
        self.fileLogger.start()
        self.fileLogger.set_status('parsing')

        # Start database inserters
        hand_inserter.start()
        player_inserter.start()
        player_hand_inserter.start()
        cache_inserter.start()

        # Create player result cache
        self.__create_cache()

        # Create a buffer for a single hand from the file
        # For efficiency we will read the file line by line and
        # add each line to the buffer until we encounter a new hand
        # When we have buffered a complete hand we kick off a parser
        # in its own thread, clear the buffer and fill it with the
        # next hand and so on until end of file
        buffer = list()
        i = 0
        self.logger.info('File: ' + self.path)
        with open(self.path, mode='r', encoding='utf-8') as f:
            for line in f:
                # the next lines are for replacing BOM
                # probably should be reading file differently but this silly code works on windows
                # need to check on linux
                if i == 0:
                    line = line.replace('\ufeff', '').strip()
                    i += 1
                # If this is the beginning of a hand then we
                # start a parser for it and continue reading the file
                if FileParser.__is_beginning_of_hand(line):
                    # Edge case for the first hand
                    # i.e. if buffer is empty
                    if len(buffer) > 0:
                        self.__start_parser(buffer)
                    # Now we can reset the buffer and start filling
                    # it with lines from the file
                    buffer = list()
                    buffer.append(line)
                else:
                    # One more line in the file that is not the first line
                    # in the next hand, just add it to the buffer
                    buffer.append(line)

        # don't forget the last hand
        if len(buffer) > 0:
            self.__start_parser(buffer)

        self.__join_parsers()
        self.cache.store()
        self.fileLogger.set_status('parsed')

    def __start_parser(self, buffer):
        if self.single_thread:
            parser = HandParserSingleThread(buffer)
            self.parsers.append(parser)
            parser.run()
        else:
            parser = HandParser(buffer)
            self.parsers.append(parser)
            parser.start()

    def __join_parsers(self):
        if not self.single_thread:
            for parser in self.parsers:
                parser.join()
        for parser in self.parsers:
            if parser.hand.verify(self.logger):
                pass
            # parser.hand.trace(self.logger)
        for parser in self.parsers:
            parser.hand.create_document()
            if not parser.hand.exists():
                parser.hand.insert()
                for player in parser.hand.players:
                    player.create_document()
                    if not player.exists():
                        player.insert()
                    player_hand = PlayerHand(parser.hand, player)
                    player_hand.create_document()
                    player_hand.insert()
                self.cache.add_hand(parser.hand)

    def __create_log(self):
        self.logger = logging.getLogger('fileparser')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2*1024*1024, backupCount=3)
        fh.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # console for dev
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def __create_cache(self):
        self.cache = Cache()
        self.cache.load()

    @staticmethod
    def __is_beginning_of_hand(text):
        return FileParser.__new_hand_regex.match(text) is not None
