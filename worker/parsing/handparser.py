from parsing.parsingutils import ParsingUtils
from handhistory.handhistory import HandHistory
from parsing.handhistorylist import HandHistoryList
from parsing.streetparser import StreetParser
from parsing.tdstreetparser import TripleDrawStreetParser

from threading import Thread
import re
import logging


class HandParser(Thread):

    def __init__(self, buffer: HandHistoryList):
        Thread.__init__(self)
        self.buffer = buffer
        self.handHistory = HandHistory()

    def run(self):
        logger = logging.getLogger('fileparser.handparser.HandParser')
        if not self.parse_header():
            logger.error('error parsing header, hand: ' + self.handHistory.handId)
            return
        if not self.parse_table():
            logger.error('error parsing table, hand: ' + self.handHistory.handId)
            return
        if not self.parse_players():
            logger.error('error parsing players, hand: ' + self.handHistory.handId)
            return
        if not self.parse_streets():
            logger.error('error parsing streets, hand: ' + self.handHistory.handId)
            return
        self.handHistory.trace(logger)
        return

    def parse_header(self):
        line = self.buffer.pop(0)
        m = re.match(ParsingUtils.regexHeader, line)
        if m:
            self.handHistory.handId = m.group('handId')
            self.handHistory.mix = m.group('mixType')
            self.handHistory.game = ParsingUtils.get_game_short_name(m.group('game'))
            self.handHistory.smallBet = m.group('smallBet')
            self.handHistory.bigBet = m.group('bigBet')
            self.handHistory.timeStamp = m.group('timeStamp')
            self.handHistory.currency = m.group('currency')
            return True
        else:
            return False

    def parse_table(self):
        line = self.buffer.pop(0)
        if self.handHistory.is_blind_game():
            m = re.match(ParsingUtils.regexTableBlindGame, line)
            if m:
                self.handHistory.tableName = m.group('tableName')
                self.handHistory.gameSize = m.group('gameSize')
                self.handHistory.buttonSeat = m.group('buttonSeat')
                return True
            else:
                return False
        else:
            m = re.match(ParsingUtils.regexTableStudGame, line)
            if m:
                self.handHistory.tableName = m.group('tableName')
                self.handHistory.gameSize = m.group('gameSize')
                return True
            else:
                return False

    def parse_players(self):
        street_text = self.buffer.pop_street()
        for line in street_text:
            m = re.match(ParsingUtils.regexPlayers, line)
            if m:
                self.handHistory.add_player(m.group('name'))
            m = re.match(ParsingUtils.regexSmallBlind, line)
            if m:
                player = self.handHistory.get_player(m.group('name'))
                player.blindAmount = m.group('amount')
                player.smallBlind = True
            m = re.match(ParsingUtils.regexBigBlind, line)
            if m:
                player = self.handHistory.get_player(m.group('name'))
                player.blindAmount = m.group('amount')
                player.bigBlind = True
            m = re.match(ParsingUtils.regexBothBlinds, line)
            if m:
                player = self.handHistory.get_player(m.group('name'))
                player.blindAmount = m.group('amount')
                player.bothBlinds = True
            m = re.match(ParsingUtils.regexAnte, line)
            if m:
                player = self.handHistory.get_player(m.group('name'))
                player.blindAmount = m.group('amount')
                player.ante = True
        return True

    def parse_streets(self):
        while ParsingUtils.get_street_name(self.buffer[0]):
            self.parse_street()
        return True

    def parse_street(self):
        line = self.buffer.pop(0)
        street_name = ParsingUtils.get_street_name(line)
        # TODO: For flop games, parse community cards
        if self.handHistory.game == 'TD':
            street_parser = TripleDrawStreetParser(street_name, self.handHistory)
            street_text = self.buffer.pop_street()
            street_parser.parse(street_text)
