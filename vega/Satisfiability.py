class Satisfiability:
    def __bool__(self):
        return False

    def __eq__(a, b):
        return a.__class__.__name__ == b.__class__.__name__

    def __repr__(self):
        return "{}".format(self.__class__.__name__.lower())

class Sat(Satisfiability):
    def __and__(self, other):
        if isinstance(other, Sat) or isinstance(other, Unknown):
            return self
        return Unsat()

    def __or__(self, other):
        return self

    def __bool__(self):
        return True

class Unsat(Satisfiability):
    def __and__(self, other):
        return self

    def __or__(self, other):
        return other

class Unknown(Satisfiability):
    def __and__(self, other):
        return other

    def __or__(self, other):
        return other