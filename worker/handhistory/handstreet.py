from handhistory.handaction import HandAction


class HandStreet:

    def __init__(self):
        self.name = ''
        self.actions = list()
        self.knownCards = list()
        self.discardedCards = list()

    def has_action(self, action: HandAction):
        for a in self.actions:
            if a.action == action:
                return True
        return False

