from pymongo import MongoClient
import logging


class FileLogger:

    def __init__(self, file_name):
        self.logger = logging.getLogger('fileparser.database.FileLogger')
        self.fileName = file_name
        self.__collection = None
        self.__id = None

    def start(self):
        client = MongoClient('mongodb://localhost:27017/')
        if not client:
            self.logger.error('error opening file log')
            return False
        self.__collection = client['fileLog']['uploaded-files']
        self.__id = self.__get_id(self.fileName)
        if not self.__id:
            self.logger.error('file not logged')
            return False
        return True

    def set_status(self, new_status):
        if not self.__id:
            self.logger.error('file not logged')
        else:
            self.__collection.update({'_id': self.__id}, {"$set": {'status': new_status}}, upsert=False)

    def __get_id(self, file_name):
        doc = self.__collection.find_one({'file': file_name})
        if doc:
            return doc['_id']
        else:
            return None
