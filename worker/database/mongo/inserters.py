from abc import ABCMeta, abstractmethod
from pymongo import MongoClient
import logging


class DatabaseInserter:
    _metaclass__ = ABCMeta

    def __init__(self, document_type):
        self.logger = logging.getLogger('fileparser.database.HandInserter')
        self.__collection = None
        self.db_id = None
        self.client = None
        self.document_type = document_type

    def start(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        if not self.client:
            self.logger.error('error opening database')
            return False
        if self.document_type == 'hand':
            self.__collection = self.client['results']['hands']
        if self.document_type == 'player':
            self.__collection = self.client['results']['players']
        if self.document_type == 'player_hand':
            self.__collection = self.client['results']['player-hands']
        return True

    def insert(self, document):
        self.db_id = self.__collection.insert_one(document).inserted_id
        return self.db_id

    def find(self, unique_field):
        doc = None
        if self.document_type == 'player':
            doc = self.__collection.find_one({'name': unique_field})
        if self.document_type == 'hand':
            doc = self.__collection.find_one({'hand_id': unique_field})
        if doc:
            return doc['_id']
        return None

hand_inserter = DatabaseInserter('hand')
player_inserter = DatabaseInserter('player')
player_hand_inserter = DatabaseInserter('player_hand')