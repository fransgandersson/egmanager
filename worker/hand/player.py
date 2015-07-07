import re
import logging
from hand.hhparser import HandHistoryParser


class Player(HandHistoryParser):

    __player_regex = re.compile("Seat (?P<seat>[\w\s]+): (?P<name>[^\r\n]+)"
                                " \((\$)?(?P<stackSize>[\w.,]+) in chips\)( is sitting out)?")
    __small_blind_regex = re.compile("(?P<name>[^\r\n]+): posts small blind (\$)?(?P<amount>[\w.,]+)([\s]+)?")
    __big_blind_regex = re.compile("(?P<name>[^\r\n]+): posts big blind (\$)?(?P<amount>[\w.,]+)([\s]+)?")
    __both_blinds_regex = re.compile("(?P<name>[^\r\n]+): posts small & big blinds (\$)?(?P<amount>[\w.,]+)([\s]+)?")
    __ante_regex = re.compile("(?P<name>[^\r\n]+): posts the ante (\$)?(?P<amount>[\w.,]+)([\s]+)?")

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.seat = None
        self.name = ''
        self.stack_size = 0
        self.blind_amount = 0
        self.small_blind = False
        self.big_blind = False
        self.both_blinds = False
        self.ante = False
        self.streets = []
        self.returned_amount = 0
        self.collected_amount = 0
        self.final_hand = []
        self.net = 0
        self.net_big_bets = 0
        self.net_big_blinds = 0
        self.saw_showdown = False
        self.position = None

    def parse(self, text_block):
        match = re.match(Player.__player_regex, text_block)
        if match:
            self.name = match.group('name')
            return True
        else:
            return False

    def parse_blinds_and_antes(self, text_block):
        for line in text_block:
            match = re.match(Player.__small_blind_regex, line)
            if match:
                if self.name == match.group('name').strip():
                    self.blind_amount = match.group('amount')
                    self.small_blind = True
            match = re.match(Player.__big_blind_regex, line)
            if match:
                if self.name == match.group('name').strip():
                    self.blind_amount = match.group('amount')
                    self.big_blind = True
            match = re.match(Player.__both_blinds_regex, line)
            if match:
                if self.name == match.group('name').strip():
                    self.blind_amount = match.group('amount')
                    self.both_blinds = True
            match = re.match(Player.__ante_regex, line)
            if match:
                if self.name == match.group('name').strip():
                    self.blind_amount = match.group('amount')
                    self.ante = True

    def trace(self, logger: logging):
        logger.debug('\t\tname: ' + self.name)
        logger.debug('\t\t\tante: ' + str(self.ante))
        logger.debug('\t\t\tposition: ' + str(self.position))
        logger.debug('\t\t\tblindAmount: ' + str(self.blind_amount))
        logger.debug('\t\t\tsmallBlind: ' + str(self.small_blind))
        logger.debug('\t\t\tbigBlind: ' + str(self.big_blind))
        logger.debug('\t\t\tbothBlinds: ' + str(self.both_blinds))
        logger.debug('\t\t\treturnedAmount: ' + str(self.returned_amount))
        logger.debug('\t\t\tcollectedAmount: ' + str(self.collected_amount))
        logger.debug('\t\t\tnet: ' + str(self.net))
        logger.debug('\t\t\tnetBigBets: ' + str(self.net_big_bets))
        logger.debug('\t\t\tnetBigBlinds: ' + str(self.net_big_blinds))
        logger.debug('\t\t\tsawShowdown: ' + str(self.saw_showdown))
        logger.debug('\t\t\tposition: ' + str(self.position))
        s = '['
        for c in self.final_hand:
            s += c
            s += ', '
        s += ']'
        logger.debug('\t\t\tfinalHand: ' + s)
        logger.debug('\t\t\tstreets:')
        for street in self.streets:
            street.trace(logger)
