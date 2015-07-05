import logging


class HandPlayer:

    def __init__(self, name):
        self.seat = None
        self.name = name
        self.stackSize = 0
        self.blindAmount = 0
        self.smallBlind = False
        self.bigBlind = False
        self.bothBlinds = False
        self.ante = False
        self.streets = []
        self.returnedAmount = 0
        self.collectedAmount = 0
        self.finalHand = []
        self.net = 0
        self.netBigBets = 0
        self.netBigBlinds = 0
        self.sawShowdown = False
        self.position = None

    def trace(self, logger: logging):
        logger.debug('\t\tname: ' + self.name)
        logger.debug('\t\t\tante: ' + str(self.ante))
        logger.debug('\t\t\tposition: ' + str(self.position))
        logger.debug('\t\t\tblindAmount: ' + str(self.blindAmount))
        logger.debug('\t\t\tsmallBlind: ' + str(self.smallBlind))
        logger.debug('\t\t\tbigBlind: ' + str(self.bigBlind))
        logger.debug('\t\t\tbothBlinds: ' + str(self.bothBlinds))
        logger.debug('\t\t\treturnedAmount: ' + str(self.returnedAmount))
        logger.debug('\t\t\tcollectedAmount: ' + str(self.collectedAmount))
        logger.debug('\t\t\tnet: ' + str(self.net))
        logger.debug('\t\t\tnetBigBets: ' + str(self.netBigBets))
        logger.debug('\t\t\tnetBigBlinds: ' + str(self.netBigBlinds))
        logger.debug('\t\t\tsawShowdown: ' + str(self.sawShowdown))
        logger.debug('\t\t\tposition: ' + str(self.position))
        logger.debug('\t\t\tfinalHand:')
        s = '['
        for c in self.finalHand:
            s += c
            s += ', '
        s += ']'
        logger.debug('\t\t\tfinalHand' + s)
        logger.debug('\t\t\tstreets:')
        for street in self.streets:
            street.trace(logger)
