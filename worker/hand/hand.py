import re
import logging
from hand.parsable import Parsable
from hand.player import Player
from hand.street import Street, TripleDrawStreet, HoldemStreet, OmahaStreet, StudStreet, ShowdownStreet
from database.mongo.storable import Storable
from database.mongo.documents import HandDocument, PlayerHandDocument

class Hand(Parsable, Storable):

    __header_regex = re.compile("PokerStars Hand #(?P<handId>[\w]+): (?P<mixType>[\w\s-]+)"
                                " \((?P<game>[\w\s'-/]+), \$(?P<smallBet>[\w.]+)/\$(?P<bigBet>[\w.]+)"
                                " (?P<currency>[\w\s]+)\) - (?P<timeStamp>[\w\s/:]+)")
    __blind_game_regex = re.compile("Table \'(?P<tableName>[^\r\n]+)\' "
                                    "((?P<gameSize>[\d]+)-max)? Seat #(?P<buttonSeat>[\d]+) is the button")
    __stud_game_regex = re.compile("Table \'(?P<tableName>[^\r\n]+)\' ((?P<gameSize>[\d]+)-max)")
    __pot_regex = re.compile(r"Total pot (\$)?(?P<potamount>[\w.,]+)( Main pot \$[\w.,]+)?( Side "
                             r"pot \$[\w.,]+)? \| Rake (\$)?(?P<rakeamount>[\w.,]+)([\s]+)?")

    def __init__(self, *args, **kwargs):
        super(Hand, self).__init__(*args, **kwargs)
        self.hand_id = ''
        self.mix = ''
        self.game = ''
        self.structure = ''
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
        self.__parse_summary_and_showdown()
        self.__post_process()

    def create_document(self):
        hd = HandDocument(self, None)
        hd.create()
        self.document = hd.document

    def exists(self):
        db_id = self.inserter.find(self.document['hand_id'])
        self.db_id = db_id
        return db_id is not None

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
            self.structure = Hand.__get_structure(self.game)
            self.small_bet = m.group('smallBet')
            self.big_bet = m.group('bigBet')
            self.time_stamp = m.group('timeStamp').strip()
            self.currency = m.group('currency')
            return True
        else:
            return False

    def __parse_table(self):
        line = self.buffer.pop(0)
        if self.is_blind_game():
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
        street_text = Parsable.pop_street(self.buffer)
        for line in street_text:
            player = Player()
            if player.parse(line):
                player.parse_blinds_and_antes(street_text)
                self.players.append(player)

    def __parse_streets(self):
        while Street.is_valid_street(self.buffer[0]):
            street_header = self.buffer.pop(0)
            street_text = Parsable.pop_street(self.buffer)
            for player in self.players:
                if self.game == 'TD':
                    street = TripleDrawStreet(street_header)
                elif self.game == 'LHE':
                    street = HoldemStreet(street_header)
                elif self.game == 'O8':
                    street = OmahaStreet(street_header)
                elif self.game == 'RAZZ':
                    street = StudStreet(street_header)
                elif self.game == 'STUD':
                    street = StudStreet(street_header)
                elif self.game == 'STUD8':
                    street = StudStreet(street_header)
                elif self.game == 'NLHE':
                    street = HoldemStreet(street_header)
                elif self.game == 'PLO':
                    street = OmahaStreet(street_header)
                else:
                    print('not a valid game!')
                player.add_street(street)
                street.parse(street_text)
                if len(street.community_cards) > 0:
                    if street.name == 'flop':
                        if len(self.flop) == 0:
                            for c in street.community_cards:
                                self.flop.append(c)
                    if street.name == 'turn':
                        if len(self.turn) == 0:
                            for c in street.community_cards:
                                self.turn.append(c)
                    if street.name == 'river':
                        if len(self.river) == 0:
                            for c in street.community_cards:
                                self.river.append(c)

    def __parse_summary_and_showdown(self):
        while len(self.buffer) > 0:
            line = self.buffer.pop(0)
            if line.strip() == Parsable._street_separators[Parsable._SUMMARY]:
                text_block = Parsable.pop_street(self.buffer)
                self.__parse_summary(text_block)
            if line.strip() == Parsable._street_separators[Parsable._SHOWDOWN]:
                text_block = Parsable.pop_street(self.buffer)
                self.__parse_showdown(text_block)

    def __parse_summary(self, text_block):
        for line in text_block:
            m = re.match(Hand.__pot_regex, line)
            if m:
                self.pot = m.group('potamount')
                self.rake = m.group('rakeamount')
                return

    def __parse_showdown(self, text_block):
        for player in self.players:
            street = ShowdownStreet()
            player.add_street(street)
            street.parse(text_block)

    def __post_process(self):
        self.__calculate_positions()
        for player in self.players:
            if player.big_blind:
                self.big_blind = player.blind_amount
            if player.small_blind:
                self.small_blind = player.blind_amount
            if self.ante == 0 and player.ante:
                self.ante = player.blind_amount
        for player in self.players:
            player.post_process(self)

    def __calculate_positions(self):
        if self.is_blind_game():
            self.__calculate_positions_blind_game()

    def __calculate_positions_blind_game(self):
        button_seat = -1
        button_player = None
        i = -1
        for player in self.players:
            i += 1
            if player.seat == self.button_seat:
                button_seat = player.seat
                player.position = 'button'
                button_player = player
                break
        if len(self.players) == 6:
            i = self.__get_next_player_index(i)
            self.players[i].position = 'sb'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'bb'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'utg'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'mp'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'co'
        if len(self.players) == 5:
            i = self.__get_next_player_index(i)
            self.players[i].position = 'sb'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'bb'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'mp'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'co'
        if len(self.players) == 4:
            i = self.__get_next_player_index(i)
            self.players[i].position = 'sb'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'bb'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'co'
        if len(self.players) == 3:
            i = self.__get_next_player_index(i)
            self.players[i].position = 'sb'
            i = self.__get_next_player_index(i)
            self.players[i].position = 'bb'
        if len(self.players) == 2:
            i = self.__get_next_player_index(i)
            self.players[i].position = 'bb'


    def __get_next_player_index(self, from_index):
        index = from_index + 1
        if len(self.players) > index:
            return index
        else:
            return 0

    def verify(self, logger: logging):
        sum_collected = float(0)
        sum_net = float(0)
        for player in self.players:
            sum_net += float(player.net)
            sum_collected += float(player.collected_amount)
        if float(sum_collected) - (float(self.pot) - float(self.rake)) > 0.001:
            logger.error('collected != pot+rake for hand: ' + self.hand_id)
            return False
        if float(sum_net) + float(self.rake) > 0.001:
            logger.error('net != rake for hand: ' + self.hand_id)
            return False
        return True

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

    @staticmethod    
    def __get_structure(game):
        if game == 'TD':
            return 'limit'
        if game == 'LHE':
            return 'limit'
        if game == 'O8':
            return 'limit'
        if game == 'RAZZ':
            return 'limit'
        if game == 'STUD':
            return 'limit'
        if game == 'STUD8':
            return 'limit'
        if game == 'NLHE':
            return 'nolimit'
        if game == 'PLO':
            return 'potlimit'
        return ''

    def is_blind_game(self):
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


class PlayerHand(Parsable, Storable):

    def __init__(self, hand: Hand, player: Player, *args, **kwargs):
        super(PlayerHand, self).__init__(*args, **kwargs)
        self.hand = hand
        self.player = player

    def parse(self, text_block):
        pass

    def create_document(self):
        hd = PlayerHandDocument(self.hand, self.player)
        hd.create()
        self.document = hd.document

    def exists(self):
        return False

    def trace(self, logger: logging):
        pass