from handhistory.handplayer import HandPlayer
import logging


class HandHistory:

    def __init__(self):
        self.handId = ''
        self.mix = ''
        self.game = ''
        self.smallBet = 0
        self.bigBet = 0
        self.smallBlind = 0
        self.bigBlind = 0
        self.ante = 0
        self.currency = ''
        self.timeStamp = ''
        self.tableName = ''
        self.gameSize = 0
        self.buttonSeat = 0
        self.pot = 0
        self.rake = 0
        self.flop = list()
        self.turn = list()
        self.river = list()
        self.players = list()
        self.sessionStartTime = ''
        self.sessionEndTime = ''

    def is_blind_game(self):
        if self.game == 'TD':
            return True
        if self.game == 'LHE':
            return True
        if self.game == 'O8':
            return True
        if self.game == 'NLHE':
            return True
        if self.game == 'PLO':
            return True
        return False

    def add_player(self, name):
        self.players.append(HandPlayer(name))

    def get_player(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    def trace(self, logger: logging):
        logger.debug('handId: ' + str(self.handId))
        logger.debug('\ttimeStamp: ' + self.timeStamp)
        logger.debug('\tsessionStartTime: ' + self.sessionStartTime)
        logger.debug('\tsessionEndTime: ' + self.sessionEndTime)
        logger.debug('\ttable: ' + self.tableName)
        logger.debug('\tmix: ' + self.mix)
        logger.debug('\tgame: ' + self.game)
        logger.debug('\tgameSize: ' + str(self.gameSize))
        logger.debug('\tstakes: $' + str(self.smallBet) + '/$' + str(self.bigBet))
        logger.debug('\tsmallBlind: ' + str(self.smallBlind))
        logger.debug('\tbigBlind: ' + str(self.bigBlind))
        logger.debug('\tante: ' + str(self.ante))
        logger.debug('\tcurrency: ' + self.currency)
        logger.debug('\tbuttonSeat: ' + str(self.buttonSeat))
        logger.debug('\tpot: ' + str(self.pot))
        logger.debug('\trake: ' + str(self.rake))
        s = '['
        for c in self.flop:
            s += c
            s += ', '
        s += ']'
        logger.debug('\tflop: ' + s)
        s = '['
        for c in self.turn:
            s += c
            s += ', '
        s += ']'
        logger.debug('\tturn: ' + s)
        s = '['
        for c in self.river:
            s += c
            s += ', '
        s += ']'
        logger.debug('\triver: ' + s)

        logger.debug('\tplayers:')
        for p in self.players:
            p.trace(logger)
