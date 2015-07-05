from abc import ABCMeta, abstractmethod
from handhistory.handhistory import HandHistory


class StreetParser:
    _metaclass__ = ABCMeta

    def __init__(self, street_name, hand_history: HandHistory):
        self.streetName = street_name
        self.handHistory = hand_history

    @abstractmethod
    def parse(self, text):
        pass
