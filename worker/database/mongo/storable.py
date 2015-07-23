from abc import ABCMeta, abstractmethod
from database.mongo.inserters import hand_inserter, player_inserter, player_hand_inserter, cache_inserter


class Storable(object):
    _metaclass__ = ABCMeta

    def __init__(self):
        super(Storable, self).__init__()
        self.db_id = None
        self.document = None
        storable_type = type(self).__name__
        if storable_type == 'Hand':
            self.inserter = hand_inserter
        if storable_type == 'Player':
            self.inserter = player_inserter
        if storable_type == 'PlayerHand':
            self.inserter = player_hand_inserter
        if storable_type == 'PlayerCache':
            self.inserter = cache_inserter

    @abstractmethod
    def create_document(self):
        pass

    def insert(self):
        self.db_id = self.inserter.insert(self.document)

    @abstractmethod
    def exists(self):
        pass
