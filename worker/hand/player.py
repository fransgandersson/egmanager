import re
import logging
from hand.parsable import Parsable
from database.mongo.storable import Storable
from database.mongo.documents import PlayerDocument


class Player(Parsable, Storable):

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
            self.seat = match.group('seat')
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

    def add_street(self, street):
        street.player = self
        self.streets.append(street)

    def post_process(self, hand):
        self.net = float(0)
        self.net += float(self.collected_amount)
        self.net += float(self.returned_amount)
        blinds_counted = False
        for street in self.streets:
            spent = float(0)
            for action in street.actions:
                if action.action == 'brings':
                    spent += float(action.amount)
                if action.action == 'bets':
                    spent += float(action.amount)
                if action.action == 'calls':
                    spent += float(action.amount)
                if action.action == 'raises':
                    if street.is_ante_street:
                        blinds_counted = True
                    # NB amount includes all previous bets and calls
                    #   hence not '+='
                    spent = float(action.to_amount)
            self.net -= float(spent)
        if hand.is_blind_game():
            if not blinds_counted:
                self.net -= float(self.blind_amount)
        else:
            self.net -= float(self.blind_amount)
        if hand.structure == 'limit':
            self.net_big_bets = float(self.net) / float(hand.big_bet)
        if hand.is_blind_game():
            self.net_big_blinds = float(self.net) / float(hand.big_blind)

    def create_document(self):
        hd = PlayerDocument(None, self)
        hd.create()
        self.document = hd.document

    def exists(self):
        db_id = self.inserter.find(self.document['name'])
        self.db_id = db_id
        return db_id is not None

    def trace(self, logger: logging):
        logger.debug('\t\tname: ' + self.name)
        logger.debug('\t\t\tante: ' + str(self.ante))
        logger.debug('\t\t\tseat: ' + str(self.seat))
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
