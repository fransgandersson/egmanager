from abc import abstractmethod
from database.mongo.storable import Storable


class PlayerCache(Storable):

    def __init__(self, game, player, *args, **kwargs):
        super(PlayerCache, self).__init__(*args, **kwargs)
        self.game = game
        self.player = player
        self.number_of_hands = float(0)
        self.net = float(0)
        self.net_big_bets = float(0)
        self.net_big_blinds = float(0)
        self.raised_preflop = float(0)
        self.put_money_in_preflop = float(0)
        self.raised_third = float(0)
        self.put_money_in_third = float(0)
        self.number_of_showdowns = float(0)
        self.won_showdown = float(0)
        self.document = None

    def __create_document(self):
        self.document = {'game': self.game,
                         'player_db_id': self.player.db_id,
                         'player_name': self.player.name,
                         'number_of_hands': self.number_of_hands,
                         'net': self.net,
                         'net_big_bets': self.net_big_bets,
                         'net_big_blinds': self.net_big_blinds,
                         'raised_preflop': self.raised_preflop,
                         'put_money_in_preflop': self.put_money_in_preflop,
                         'raised_third': self.raised_third,
                         'put_money_in_third': self.put_money_in_third,
                         'number_of_showdowns': self.number_of_showdowns,
                         'won_showdown': self.won_showdown}

    @abstractmethod
    def create_document(self):
        self.__create_document()

    def store(self):
        self.db_id = self.inserter.upsert(self.document, {'game': self.game, 'player_name': self.player.name})

    @abstractmethod
    def exists(self):
        pass


class Cache:

    def __init__(self):
        self.player_caches = list()

    def load(self):
        pass

    def store(self):
        for player_cache in self.player_caches:
            player_cache.create_document()
            player_cache.store()

    def add_hand(self, hand):
        for player in hand.players:
            player_cache = self.__get_player_cache(hand.game, player)
            if player_cache is None:
                player_cache = PlayerCache(hand.game, player)
                self.player_caches.append(player_cache)
            player_cache.number_of_hands += 1
            player_cache.net += float(player.net)
            player_cache.net_big_bets += float(player.net_big_bets)
            player_cache.net_big_blinds += float(player.net_big_blinds)
            if player.saw_showdown:
                player_cache.number_of_showdowns += 1
                if player.net > 0.001:
                    player_cache.won_showdown += 1
            for street in player.streets:
                if street.name == 'preflop':
                    for a in street.actions:
                        if (a.action == 'calls') or (a.action == 'raises'):
                            player_cache.put_money_in_preflop += 1
                        if a.action == 'raises':
                            player_cache.raised_preflop += 1
                if street.name == 'third':
                    for a in street.actions:
                        if (a.action == 'calls') or (a.action == 'raises'):
                            player_cache.put_money_in_third += 1
                        if a.action == 'raises':
                            player_cache.raised_third += 1

    def __get_player_cache(self, game, player):
        for player_cache in self.player_caches:
            if player_cache.player.db_id == player.db_id:
                if player_cache.game == game:
                    return player_cache
        return None
