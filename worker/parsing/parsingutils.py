import re


class ParsingUtils:

    regexNewHand = re.compile("PokerStars Hand #([\w]+): ")
    regexHeader = re.compile("PokerStars Hand #(?P<handId>[\w]+): (?P<mixType>[\w\s-]+)"
                             " \((?P<game>[\w\s'-/]+), \$(?P<smallBet>[\w.]+)/\$(?P<bigBet>[\w.]+)"
                             " (?P<currency>[\w\s]+)\) - (?P<timeStamp>[\w\s/:]+)")
    regexTableBlindGame = re.compile("Table \'(?P<tableName>[^\r\n]+)\' "
                                     "((?P<gameSize>[\d]+)-max)? Seat #(?P<buttonSeat>[\d]+) is the button")
    regexTableStudGame = re.compile("Table \'(?P<tableName>[^\r\n]+)\' ((?P<gameSize>[\d]+)-max)")
    regexPlayers = re.compile("Seat (?P<seat>[\w\s]+): (?P<name>[^\r\n]+)"
                              " \((\$)?(?P<stackSize>[\w.,]+) in chips\)( is sitting out)?")
    regexSmallBlind = re.compile("(?P<name>[^\r\n]+): posts small blind (\$)?(?P<amount>[\w.,]+)([\s]+)?")
    regexBigBlind = re.compile("(?P<name>[^\r\n]+): posts big blind (\$)?(?P<amount>[\w.,]+)([\s]+)?")
    regexBothBlinds = re.compile("(?P<name>[^\r\n]+): posts small & big blinds (\$)?(?P<amount>[\w.,]+)([\s]+)?")
    regexAnte = re.compile("(?P<name>[^\r\n]+): posts the ante (\$)?(?P<amount>[\w.,]+)([\s]+)?")

    streetSeparators = ['*** DEALING HANDS ***',
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

    @staticmethod
    def is_beginning_of_hand(text):
        return ParsingUtils.regexNewHand.match(text) is not None

    @staticmethod
    def get_game_short_name(game):
        g = game.strip()
        if g == 'Triple Draw 2-7 Lowball Limit':
            return 'TD'
        if g == 'Hold\'em Limit':
            return 'LHE'
        if g == 'Omaha Hi/Lo Limit':
            return 'O8'
        if g == 'Hold\'em No Limit':
            return 'NLHE'
        if g == 'Omaha Pot Limit':
            return 'PLO'
        if g == 'Razz Limit':
            return 'RAZZ'
        if g == '7 Card Stud Limit':
            return 'STUD'
        if g == '7 Card Stud Hi/Lo Limit':
            return 'STUD8'
        return ''

    @staticmethod
    def get_street_name(text):
        # TODO: Fix to remove community cards
        s = text.strip()
        if s == '*** DEALING HANDS ***':
            return 'preflop'
        if s == '*** HOLE CARDS ***':
            return 'preflop'
        if s == '*** FIRST DRAW ***':
            return 'flop'
        if s == '*** FLOP ***':
            return 'flop'
        if s == '*** SECOND DRAW ***':
            return 'turn'
        if s ==  '*** TURN ***':
            return 'turn'
        if s ==  '*** THIRD DRAW ***':
            return 'river'
        if s ==  '*** RIVER ***':
            return 'river'
        if s ==  '*** 3rd STREET ***':
            return 'third'
        if s ==  '*** 4th STREET ***':
            return 'fourth'
        if s ==  '*** 5th STREET ***':
            return 'fifth'
        if s ==  '*** 6th STREET ***':
            return 'sixth'
        return None