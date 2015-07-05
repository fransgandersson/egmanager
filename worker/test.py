import parsing.parsingutils
import parsing.fileparser
import os

s = "PokerStars Hand #136693341308:  8-Game " \
    "(Hold'em Limit, $1/$2 USD) - 2015/06/14 10:09:36 WET [2015/06/14 5:09:36 ET]"
s2 = "not a hand"
m = parsing.parsingutils.ParsingUtils.is_beginning_of_hand(s)
print(m)
m = parsing.parsingutils.ParsingUtils.is_beginning_of_hand(s2)
print(m)
path = "HH20120414 Megaira V - $1-$2 - USD 8-Game.txt"
fp = parsing.fileparser.FileParser(os.path.abspath('../webserver/uploads/'), 'f0719f0fac13a5b1f4bf0e38ee3cd196.txt')
fp.parse()