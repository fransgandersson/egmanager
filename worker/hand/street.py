import re
import logging
from hand.hhparser import HandHistoryParser


class Action:

    def __init__(self):
        self.index = 0
        self.action = ''
        self.amount = 0
        self.to_amount = 0

    def trace(self, logger: logging):
        logger.debug('\t\t\t\t\tindex: ' + str(self.index))
        logger.debug('\t\t\t\t\taction: ' + self.action)
        logger.debug('\t\t\t\t\tamount: ' + str(self.amount))
        logger.debug('\t\t\t\t\tto_amount: ' + str(self.to_amount))


class Street(HandHistoryParser):

    _dealt_to_regex = re.compile(r"Dealt to (?P<name>[^\r\n]+?) \[.*")
    _action_regex = re.compile(r"(?P<name>[^\r\n]+): (?P<action>\b(folds|raises|calls|bets|checks|brings)\b)"
                               r"( (in for )?(\$)(?P<amount>[\d.,]+))?( to (\$)(?P<toamount>[\d.,]+))?")
    _card_regex = re.compile(r"(?P<card>[\d|T|J|Q|K|A][h|s|c|d])[\s|\]]")

    def __init__(self, players: list, header: str, *args, **kwargs):
        super(Street, self).__init__(*args, **kwargs)
        self.name = Street.__get_street_name(header)
        self.players = players
        self.actions = list()
        self.cards = list()
        self.discards = list()
        self.community_cards = list()

    def parse(self, text_block):
        pass

    def trace(self, logger: logging):
        logger.debug('\t\t\t\tname: ' + self.name)
        s = '['
        for c in self.cards:
            s += c
            s += ', '
        s += ']'
        logger.debug('\t\t\t\tcards: ' + s)
        s = '['
        for c in self.discards:
            s += c
            s += ', '
        s += ']'
        logger.debug('\t\t\t\tdiscards: ' + s)
        logger.debug('\t\t\t\tactions:')
        for action in self.actions:
            action.trace(logger)

    @staticmethod
    def is_valid_street(line):
        return Street.__get_street_name(line) is not None

    @staticmethod
    def __get_street_name(text):
        # TODO: Fix to remove community cards
        s = text.strip()
        if s == '*** DEALING HANDS ***':
            return 'preflop'
        if s == '*** HOLE CARDS ***':
            return 'preflop'
        if s == '*** FIRST DRAW ***':
            return 'flop'
        if s == '*** FLOP ***':
            return 'flop'
        if s == '*** SECOND DRAW ***':
            return 'turn'
        if s == '*** TURN ***':
            return 'turn'
        if s == '*** THIRD DRAW ***':
            return 'river'
        if s == '*** RIVER ***':
            return 'river'
        if s == '*** 3rd STREET ***':
            return 'third'
        if s == '*** 4th STREET ***':
            return 'fourth'
        if s == '*** 5th STREET ***':
            return 'fifth'
        if s == '*** 6th STREET ***':
            return 'sixth'
        return None


class TripleDrawStreet(Street, HandHistoryParser):

    def parse(self, text_block):
        if self.name == 'preflop':
            self.__parse_predraw(text_block)

    def trace(self, logger: logging):
        super(TripleDrawStreet, self).trace(logger)

    def __parse_predraw(self, text_block):
        action_index = 0;
        while len(text_block) > 0:
            line = text_block.pop(0)
            match = re.match(Street._dealt_to_regex, line)
            if match:
                self.__get_player(match.group('name')).streets.append(self)
                match = re.findall(Street._card_regex, line)
                if match:
                    for c in match:
                        self.cards.append(c)
            match = re.match(Street._action_regex, line)
            if match:
                action = Action()
                action.index = action_index
                action.action = match.group('action')
                action.amount = match.group('amount')
                action.to_amount = match.group('toamount')
                player = self.__get_player(match.group('name'))
                # TODO: continue...
                action_index += 1


    def __get_player(self, name):
        for p in self.players:
            if p.name == name:
                return p

    def __get_player_street(self, player):
        for street in player.streets:
            if street.name == self.name:
                return street
        return None
