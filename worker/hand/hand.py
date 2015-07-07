import re
import logging
from hand.hhparser import HandHistoryParser
from hand.player import Player
from hand.street import Street, TripleDrawStreet


class Hand(HandHistoryParser):

    __header_regex = re.compile("PokerStars Hand #(?P<handId>[\w]+): (?P<mixType>[\w\s-]+)"
                                " \((?P<game>[\w\s'-/]+), \$(?P<smallBet>[\w.]+)/\$(?P<bigBet>[\w.]+)"
                                " (?P<currency>[\w\s]+)\) - (?P<timeStamp>[\w\s/:]+)")
    __blind_game_regex = re.compile("Table \'(?P<tableName>[^\r\n]+)\' "
                                    "((?P<gameSize>[\d]+)-max)? Seat #(?P<buttonSeat>[\d]+) is the button")
    __stud_game_regex = re.compile("Table \'(?P<tableName>[^\r\n]+)\' ((?P<gameSize>[\d]+)-max)")

    def __init__(self, *args, **kwargs):
        super(Hand, self).__init__(*args, **kwargs)
        self.hand_id = ''
        self.mix = ''
        self.game = ''
        self.small_bet = 0
        self.big_bet = 0
        self.small_blind = 0
        self.big_blind = 0
        self.ante = 0
        self.currency = ''
        self.time_stamp = ''
        self.table_name = ''
        self.game_size = 0
        self.button_seat = 0
        self.pot = 0
        self.rake = 0
        self.flop = list()
        self.turn = list()
        self.river = list()
        self.players = list()
        self.session_start_time = ''
        self.session_end_time = ''
        self.buffer = None

    def parse(self, text_block):
        self.buffer = text_block
        self.__parse_header()
        self.__parse_table()
        self.__parse_players()
        self.__parse_streets()

    def trace(self, logger: logging):
        logger.debug('handId: ' + str(self.hand_id))
        logger.debug('\ttimeStamp: ' + self.time_stamp)
        logger.debug('\tsessionStartTime: ' + self.session_start_time)
        logger.debug('\tsessionEndTime: ' + self.session_end_time)
        logger.debug('\ttable: ' + self.table_name)
        logger.debug('\tmix: ' + self.mix)
        logger.debug('\tgame: ' + self.game)
        logger.debug('\tgameSize: ' + str(self.game_size))
        logger.debug('\tstakes: $' + str(self.small_bet) + '/$' + str(self.big_bet))
        logger.debug('\tsmallBlind: ' + str(self.small_blind))
        logger.debug('\tbigBlind: ' + str(self.big_blind))
        logger.debug('\tante: ' + str(self.ante))
        logger.debug('\tcurrency: ' + self.currency)
        logger.debug('\tbuttonSeat: ' + str(self.button_seat))
        logger.debug('\tpot: ' + str(self.pot))
        logger.debug('\trake: ' + str(self.rake))
        s = '['
        for c in self.flop:
            s += c
            s += ', '
        s += ']'
        logger.debug('\tflop: ' + s)
        s = '['
        for c in self.turn:
            s += c
            s += ', '
        s += ']'
        logger.debug('\tturn: ' + s)
        s = '['
        for c in self.river:
            s += c
            s += ', '
        s += ']'
        logger.debug('\triver: ' + s)

        logger.debug('\tplayers:')
        for p in self.players:
            p.trace(logger)

    def __parse_header(self):
        line = self.buffer.pop(0)
        m = re.match(Hand.__header_regex, line)
        if m:
            self.hand_id = m.group('handId')
            self.mix = m.group('mixType')
            self.game = Hand.__get_game_short_name(m.group('game'))
            self.small_bet = m.group('smallBet')
            self.big_bet = m.group('bigBet')
            self.time_stamp = m.group('timeStamp')
            self.currency = m.group('currency')
            return True
        else:
            return False

    def __parse_table(self):
        line = self.buffer.pop(0)
        if self.__is_blind_game():
            m = re.match(Hand.__blind_game_regex, line)
            if m:
                self.table_name = m.group('tableName')
                self.game_size = m.group('gameSize')
                self.button_seat = m.group('buttonSeat')
                return True
            else:
                return False
        else:
            m = re.match(Hand.__stud_game_regex, line)
            if m:
                self.table_name = m.group('tableName')
                self.game_size = m.group('gameSize')
                return True
            else:
                return False

    def __parse_players(self):
        street_text = self.buffer.pop_street()
        for line in street_text:
            player = Player()
            if player.parse(line):
                player.parse_blinds_and_antes(street_text)
                self.players.append(player)

    def __parse_streets(self):
        while Street.is_valid_street(self.buffer[0]):
            if self.game == 'TD':
                street = TripleDrawStreet(self.players, self.buffer.pop(0))
                street.parse(self.buffer.pop_street())
            else:
                street = Street(self.players, self.buffer.pop(0))
                street.parse(self.buffer.pop_street())

    def __is_blind_game(self):
        if self.game == 'TD':
            return True
        if self.game == 'LHE':
            return True
        if self.game == 'O8':
            return True
        if self.game == 'NLHE':
            return True
        if self.game == 'PLO':
            return True
        return False

    @staticmethod
    def __get_game_short_name(game):
        g = game.strip()
        if g == 'Triple Draw 2-7 Lowball Limit':
            return 'TD'
        if g == 'Hold\'em Limit':
            return 'LHE'
        if g == 'Omaha Hi/Lo Limit':
            return 'O8'
        if g == 'Hold\'em No Limit':
            return 'NLHE'
        if g == 'Omaha Pot Limit':
            return 'PLO'
        if g == 'Razz Limit':
            return 'RAZZ'
        if g == '7 Card Stud Limit':
            return 'STUD'
        if g == '7 Card Stud Hi/Lo Limit':
            return 'STUD8'
        return ''
