from abc import ABCMeta, abstractmethod


class Document:
    _metaclass__ = ABCMeta

    def __init__(self, hand, player):
        self.hand = hand
        self.player = player
        self.document = None

    @abstractmethod
    def create(self):
        pass


class StakeDocument(Document):

    def create(self):
        self.document = {'structure': self.hand.structure,
                    'small_bet': self.hand.small_bet,
                    'big_bet': self.hand.big_bet,
                    'small_blind': self.hand.small_blind,
                    'big_blind': self.hand.big_blind,
                    'ante': self.hand.ante,
                    'max_buyin': 0,
                    'currency': 'USD'}


class TableSessionDocument(Document):

    def create(self):
        self.document = {'table_name': self.hand.table_name,
                    'start_time': self.hand.session_start_time,
                    'end_time': self.hand.session_end_time,
                    'size': self.hand.game_size}


class HandDocument(Document):

    def create(self):
        stake_document = StakeDocument(self.hand, None)
        stake_document.create()
        session_document = TableSessionDocument(self.hand, None)
        session_document.create()
        self.document = {'hand_id': self.hand.hand_id,
                         'site': 'pokerstars',
                         'game': self.hand.game,
                         'mix': self.hand.mix,
                         'time_stamp': self.hand.time_stamp,
                         'number_of_players': len(self.hand.players),
                         'pot': self.hand.pot,
                         'rake': self.hand.rake,
                         'stake': stake_document.document,
                         'table_session': session_document.document,
                         'flop': self.__get_street_document('flop'),
                         'turn': self.__get_street_document('turn'),
                         'river': self.__get_street_document('river')}

    def __get_street_document(self, street_name):
        street_document = list()
        card_list = list()
        if street_name == 'flop':
            card_list = self.hand.flop
        if street_name == 'turn':
            card_list = self.hand.turn
        if street_name == 'river':
            card_list = self.hand.river

        for c in card_list:
            street_document.append(c)
        return street_document


class PlayerDocument(Document):

    def create(self):
        self.document = {'name': self.player.name,
                    'site': 'pokerstars'}


class PlayerHandDocument(Document):

    def create(self):
        self.document = {'player_id': self.player.db_id,
                         'hand_id': self.hand.db_id,
                         'went_to_showdown': self.player.saw_showdown,
                         'net': self.player.net,
                         'net_big_bets': self.player.net_big_bets,
                         'net_big_blinds': self.player.net_big_blinds,
                         'won': (float(self.player.collected_amount) > 0.0001),
                         'seat': self.player.seat,
                         'position': self.player.position}