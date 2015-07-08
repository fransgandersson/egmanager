from hand.hand import Hand
from threading import Thread
import logging


class HandParser(Thread):

    def __init__(self, buffer: list):
        Thread.__init__(self)
        self.buffer = buffer

    def run(self):
        logger = logging.getLogger('fileparser.handparser.HandParser')
        hand = Hand()
        hand.parse(self.buffer)
        hand.trace(logger)


class HandParserSingleThread():

    def __init__(self, buffer: list):
        self.buffer = buffer

    def run(self):
        logger = logging.getLogger('fileparser.handparser.HandParser')
        hand = Hand()
        hand.parse(self.buffer)
        hand.trace(logger)
