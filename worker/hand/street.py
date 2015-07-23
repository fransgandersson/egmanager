import re
import logging
from hand.parsable import Parsable


class Action:

    def __init__(self, name=''):
        self.index = 0
        self.action = name
        self.amount = 0
        self.to_amount = 0

    def trace(self, logger: logging):
        logger.debug('\t\t\t\t\tindex: ' + str(self.index))
        logger.debug('\t\t\t\t\taction: ' + self.action)
        logger.debug('\t\t\t\t\tamount: ' + str(self.amount))
        logger.debug('\t\t\t\t\tto_amount: ' + str(self.to_amount))


class Street(Parsable):

    _dealt_to_regex = re.compile(r"Dealt to (?P<name>[^\r\n]+?) \[.*")
    _action_regex = re.compile(r"(?P<name>[^\r\n]+): (?P<action>\b(folds|raises|calls|bets|checks|brings)\b)"
                               r"( (in for )?(\$)(?P<amount>[\d.,]+))?( to (\$)(?P<toamount>[\d.,]+))?")
    _card_regex = re.compile(r"(?P<card>[\d|T|J|Q|K|A][h|s|c|d])[\s|\]]")
    _draw_regex = re.compile(r"(?P<name>[^\r\n]+): ((discards ?(?P<amount>[\w.,]+) "
                             r"card[s]*([\s]+)?(\[.*\])?)|(stands pat))")
    _bet_returned_regex = re.compile(r"Uncalled bet \((\$)?(?P<amount>[\w.,]+)\) "
                                     r"returned to (?P<name>[^\r\n]+)([\s]+)?")
    _collected_regex = re.compile(r"(?P<name>[^\r\n]+) collected (\$)?"
                                  r"(?P<amount>[\w.,]+) from( main)?( side)? pot([\s]+)?")
    _action_index = 0

    def __init__(self, header):
        super(Street, self).__init__()
        self.name = ''
        self.actions = list()
        self.cards = list()
        self.discards = list()
        self.community_cards = list()
        self.player = None
        self.is_ante_street = False
        self.header = header

    def parse(self, text_block):
        pass

    def trace(self, logger: logging):
        logger.debug('\t\t\t\tname: ' + self.name)
        s = '['
        for c in self.community_cards:
            s += c
            s += ', '
        s += ']'
        logger.debug('\t\t\t\tcommunity_cards: ' + s)
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
        return Street._get_street_name(line) is not None

    @staticmethod
    def _get_street_name(text):
        s = text.strip()
        n = s.find('[')
        if n != -1:
            s = s[:n-1].strip()
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

    def _parse_header(self):
        if self.header:
            m = re.findall(Street._card_regex, self.header)
            if m:
                for c in m:
                    self.community_cards.append(c)
            self.name = Street._get_street_name(self.header)

    def _parse_dealt_cards(self, line):
        match = re.match(Street._dealt_to_regex, line)
        if match:
            if match.group('name') == self.player.name:
                match = re.findall(Street._card_regex, line)
                if match:
                    for c in match:
                        self.cards.append(c)

    def _parse_action(self, line):
        match = re.match(Street._action_regex, line)
        if match:
            if match.group('name') == self.player.name:
                action = Action()
                action.index = self._action_index
                action.action = match.group('action')
                action.amount = match.group('amount')
                action.to_amount = match.group('toamount')
                self.actions.append(action)
            self._action_index += 1

    def _parse_bet_returned(self, line):
        match = re.match(Street._bet_returned_regex, line)
        if match:
            if match.group('name') == self.player.name:
                self.player.returned_amount = match.group('amount')

    def _parse_collected(self, line):
        self.player.collected_amount = float(0)
        match = re.match(Street._collected_regex, line)
        if match:
            if match.group('name') == self.player.name:
                self.player.collected_amount += float(match.group('amount'))


class TripleDrawStreet(Street, Parsable):

    def parse(self, text_block):
        buffer = list(text_block)
        self._parse_header()
        if self.name == 'preflop':
            self.is_ante_street = True
            self.__parse_predraw(buffer)
        if self.name == 'flop':
            self.__parse_draw(buffer)
        if self.name == 'turn':
            self.__parse_draw(buffer)
        if self.name == 'river':
            self.__parse_draw(buffer)

    def trace(self, logger: logging):
        super(TripleDrawStreet, self).trace(logger)

    def __parse_predraw(self, buffer):
        while len(buffer) > 0:
            line = buffer.pop(0)
            self._parse_dealt_cards(line)
            self._parse_action(line)
            self._parse_bet_returned(line)
            self._parse_collected(line)

    def __parse_draw(self, buffer):
        while len(buffer) > 0:
            line = buffer.pop(0)
            self.__parse_discards(line)
            self._parse_dealt_cards(line)
            self._parse_action(line)
            self._parse_bet_returned(line)
            self._parse_collected(line)

    def __parse_discards(self, line):
        match = re.match(Street._draw_regex, line)
        if match:
            if match.group('name') == self.player.name:
                if match.group('amount') and int(match.group('amount')) > 0:
                    pat = False
                else:
                    pat = True
                match = re.findall(Street._card_regex, line)
                if match:
                    for c in match:
                        if pat:
                            self.cards.append(c)
                        else:
                            self.discards.append(c)


class HoldemStreet(Street, Parsable):

    def parse(self, text_block):
        buffer = list(text_block)
        self._parse_header()
        if self.name == 'preflop':
            self.is_ante_street = True
            self._parse_preflop(buffer)
        if self.name == 'flop':
            self._parse_postflop(buffer)
        if self.name == 'turn':
            self._parse_postflop(buffer)
        if self.name == 'river':
            self._parse_postflop(buffer)

    def trace(self, logger: logging):
        super(HoldemStreet, self).trace(logger)

    def _parse_preflop(self, buffer):
        while len(buffer) > 0:
            line = buffer.pop(0)
            self._parse_dealt_cards(line)
            self._parse_action(line)
            self._parse_bet_returned(line)
            self._parse_collected(line)

    def _parse_postflop(self, buffer):
        while len(buffer) > 0:
            line = buffer.pop(0)
            self._parse_action(line)
            self._parse_bet_returned(line)
            self._parse_collected(line)


class OmahaStreet(HoldemStreet, Parsable):

    def parse(self, text_block):
        super(OmahaStreet, self).parse(text_block)

    def trace(self, logger: logging):
        super(OmahaStreet, self).trace(logger)


class StudStreet(Street, Parsable):

    def parse(self, text_block):
        self._parse_header()
        if self.name == 'third':
            self.is_ante_street = True
        buffer = list(text_block)
        while len(buffer) > 0:
            line = buffer.pop(0)
            self._parse_dealt_cards(line)
            self._parse_action(line)
            self._parse_bet_returned(line)
            self._parse_collected(line)

    def trace(self, logger: logging):
        super(StudStreet, self).trace(logger)


class ShowdownStreet(Street, Parsable):

    __show_regex = re.compile(r"(?P<name>[^\r\n]+): show([\s]+)?")
    __muck_regex = re.compile(r"(?P<name>[^\r\n]+): mucks hand([\s]+)?")

    def __init__(self, *args, **kwargs):
        super(ShowdownStreet, self).__init__(None, *args, **kwargs)

    def parse(self, text_block):
        buffer = list(text_block)
        self.name = 'showdown'
        while len(buffer) > 0:
            line = buffer.pop(0)
            self._parse_collected(line)
            self.__parse_show(line)
            self.__parse_muck(line)

    def trace(self, logger: logging):
        super(ShowdownStreet, self).trace(logger)

    def __parse_show(self, line):
        match = re.match(ShowdownStreet.__show_regex, line)
        if match:
            if match.group('name') == self.player.name:
                self.player.saw_showdown = True
                self.actions.append(Action('show'))
                match = re.findall(Street._card_regex, line)
                if match:
                    for c in match:
                        self.cards.append(c)
                        self.player.final_hand.append(c)

    def __parse_muck(self, line):
        match = re.match(ShowdownStreet.__muck_regex, line)
        if match:
            if match.group('name') == self.player.name:
                self.actions.append(Action('muck'))
                self.player.saw_showdown = True
