from abc import ABCMeta, abstractmethod
import logging


class HandHistoryList(list):

    def pop_street(self):
        return_buffer = list()
        while len(self) > 0:
            line = self.pop(0).strip()
            if line in HandHistoryParser.street_separators:
                # put line back on top
                self.insert(0, line)
                return return_buffer
            else:
                return_buffer.append(line)

        return None


class HandHistoryParser:
    _metaclass__ = ABCMeta

    street_separators = ['*** DEALING HANDS ***',
                         '*** FIRST DRAW ***',
                         '*** SECOND DRAW ***',
                         '*** THIRD DRAW ***',
                         '*** SHOW DOWN ***',
                         '*** SUMMARY ***',
                         '*** HOLE CARDS ***',
                         '*** FLOP ***',
                         '*** TURN ***',
                         '*** RIVER ***',
                         '*** 3rd STREET ***',
                         '*** 4th STREET ***',
                         '*** 5th STREET ***',
                         '*** 6th STREET ***']

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def parse(self, text_block):
        pass

    @abstractmethod
    def trace(self, logger: logging):
        pass