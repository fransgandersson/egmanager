import parsing.fileparser
import os

# fp = parsing.fileparser.FileParser(os.path.abspath('../webserver/uploads/'), 'f0719f0fac13a5b1f4bf0e38ee3cd196.txt')
fp = parsing.fileparser.FileParser(os.path.abspath('./test_files'), 'HH20120413 Buryatia - $1-$2 - USD 8-Game.txt')
fp.parse()