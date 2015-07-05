from parsing.parsingutils import ParsingUtils
from parsing.handparser import HandParser
from parsing.handhistorylist import HandHistoryList
from database.filelogger import FileLogger
import logging
from logging import handlers
import os

LOG_FILENAME = 'fileparser.log'


class FileParser:

    def __init__(self, folder, file_name):
        self.parsers = list()
        self.logger = None
        self.path = os.path.join(folder, file_name)
        self.fileLogger = FileLogger(file_name)

    def parse(self):
        # Create error log
        self.create_log()

        # Start the file log
        # The file log contains the
        # file we are currently parsing
        # It can be implemented e.g. as a database
        # Update its status to 'parsing'
        self.fileLogger.start()
        self.fileLogger.set_status('parsing')

        # Create a buffer for a single hand from the file
        # For efficiency we will read the file line by line and
        # add each line to the buffer until we encounter a new hand
        # When we have buffered a complete hand we kick off a parser
        # in its own thread, clear the buffer and fill it with the
        # next hand and so on until end of file
        buffer = HandHistoryList()
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
                if ParsingUtils.is_beginning_of_hand(line):
                    # Edge case for the first hand
                    # i.e. if buffer is empty
                    if len(buffer) > 0:
                        self.start_parser(buffer)
                    # Now we can reset the buffer and start filling
                    # it with lines from the file
                    buffer = HandHistoryList()
                    buffer.append(line)
                else:
                    # One more line in the file that is not the first line
                    # in the next hand, just add it to the buffer
                    buffer.append(line)

        # don't forget the last hand
        if len(buffer) > 0:
            self.start_parser(buffer)

        self.join_parsers()
        self.fileLogger.set_status('parsed')

    def start_parser(self, buffer):
        parser = HandParser(buffer)
        self.parsers.append(parser)
        parser.start()

    def join_parsers(self):
        for parser in self.parsers:
            parser.join()

    def create_log(self):
        self.logger = logging.getLogger('fileparser')
        self.logger.setLevel(logging.WARNING)
        fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2*1024*1024, backupCount=3)
        fh.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # console for dev
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
