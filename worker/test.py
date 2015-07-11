import parsing.fileparser
import os

# fp = parsing.fileparser.FileParser(os.path.abspath('../webserver/uploads/'), 'f0719f0fac13a5b1f4bf0e38ee3cd196.txt')
# fp = parsing.fileparser.FileParser(os.path.abspath(''), 'td.txt')
# fp.parse()

fp = parsing.fileparser.FileParser(os.path.abspath(''), 'lhe.txt')
fp.parse()