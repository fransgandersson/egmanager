from hand.hand import Hand
from threading import Thread
import logging


class HandParser(Thread):

    def __init__(self, buffer: list):
        Thread.__init__(self)
        self.buffer = buffer
        self.hand = Hand()

    def run(self):
        logger = logging.getLogger('fileparser.handparser.HandParser')
        self.hand.parse(self.buffer)


class HandParserSingleThread():

    def __init__(self, buffer: list):
        self.buffer = buffer
        self.hand = Hand()

    def run(self):
        logger = logging.getLogger('fileparser.handparser.HandParser')
        self.hand.parse(self.buffer)
