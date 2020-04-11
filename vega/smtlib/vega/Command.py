class Command:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.name, self.args)