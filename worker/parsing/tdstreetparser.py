from parsing.streetparser import StreetParser


class TripleDrawStreetParser(StreetParser):

    def parse(self, text):
        print(self.streetName)
        print(text)
        if self.streetName == 'preflop':
            self.__parse_pre_draw()
        else:
            self.__parse_draw()

    def __parse_pre_draw(self):
        pass

    def __parse_draw(self):
        pass
