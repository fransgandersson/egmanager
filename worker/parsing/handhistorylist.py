from parsing.parsingutils import ParsingUtils


class HandHistoryList(list):

    def pop_street(self):
        return_buffer = list()
        while len(self) > 0:
            line = self.pop(0).strip()
            if line in ParsingUtils.streetSeparators:
                # put line back on top
                self.insert(0, line)
                return return_buffer
            else:
                return_buffer.append(line)

        return None

