# stores information about the trace table. this includes the actual table, which is stored as a dictionary called
# traceDict. The keys are the variable names (the 'columns' visually) and the values are the series of each value that
# variable took at each step in the program (each row for that column visually).
# additionally, the length is stored so to identify by how much blank cells to pad a value of a variable when it is
# added for the first time to the trace table.
# there is a method to find the visual width of the trace table, which is just the sum of the sizes taken up by the
# column headers (i.e., each variable name), plus the padding on each side of the variable name
# and there is another method to find the visual height, through adding the standard height of a character to the
# sum of the padding on the top and bottom, and then multiplying that by the length of the trace table.
# there are also getter methods to get, for the trace so far, the variables, the number of variables and the contents
# of a column (accessed through the key, which is the header of that column, i.e., the variable for that column).
# these methods allow for traceDict to be private to the class so it can't be accessed/modified outside class instances.
class TraceTable:
    def __init__(self):
        self.__traceDict = {}
        self.length = 1

    def update(self, varName, value):
        if varName not in self.__traceDict:
            self.__traceDict[varName] = [None for _ in range(self.length)]
            self.__traceDict[varName][-1] = value
        else:
            if self.__traceDict[varName][-1] is not None:
                for key in self.__traceDict.keys():
                    self.__traceDict[key].append(None)
                self.__traceDict[varName][-1] = value
                self.length += 1
            else:
                self.__traceDict[varName][-1] = value

    def get_vars(self):
        return self.__traceDict.keys()

    def get_num_vars(self):
        return len(self.__traceDict)

    def get_column(self, key):
        return self.__traceDict[key]

    def width(self, font):
        return sum(font.size(x)[0] for x in self.__traceDict.keys()) + 10 * len(self.__traceDict.keys())

    def height(self, char_height):
        return (char_height + 10) * self.length

