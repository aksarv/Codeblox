class GlobalsStack:
    def __init__(self):
        # initialise stack with global context only - only needs to be accessed privately
        self.__stack = [{}]

    # __getitem__ and __setitem__ are overridden here to allow for custom behaviour when values are accessed/modified
    # e.g. a = GlobalsStack(); a[1]
    # above would invoke __getitem__ on an index of 1
    # e.g. a = GlobalsStack(); a[1] = 2
    # above would invoke __setitem__ on an index of 1 with a value of 2
    def __getitem__(self, i):
        # see if the variable is present in any previous contexts, most recent first - if so we return it
        # if not, the variable is not defined in scope or at all so a KeyError is raised
        for f in self.__stack[::-1]:
            try:
                return f[i]
            except KeyError:
                pass
        raise KeyError(f'{i}')

    def __setitem__(self, i, v):
        # see if the variable is present in any previous contexts, most recent first - if so we update only this value
        for f in self.__stack[::-1]:
            if i in f:
                f[i] = v
                break
        else:
            # if no such contexts found, add it as a new variable in the current context
            self.__stack[-1][i] = v

    def push(self):
        # add new context
        self.__stack.append({})

    def pop(self):
        # remove existing context - only allowed if length of stack is larger than 1 since you can't get rid of the
        # global context (outermost)
        if len(self.__stack) > 1:
            self.__stack.pop(len(self.__stack) - 1)

    def reset(self):
        # reset the globals stack when all code has run so variables are not accessed from previous runs
        self.__stack = [{}]

