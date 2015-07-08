from abc import ABCMeta, abstractmethod
import logging


class HandHistoryParser:
    _metaclass__ = ABCMeta

    __street_separators = ['*** DEALING HANDS ***',
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

    @staticmethod
    def pop_street(text_block: list):
        return_buffer = list()
        while len(text_block) > 0:
            line = text_block.pop(0).strip()
            if line in HandHistoryParser.__street_separators:
                # put line back on top
                text_block.insert(0, line)
                return return_buffer
            else:
                return_buffer.append(line)

        return None

