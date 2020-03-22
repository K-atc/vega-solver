class Tactic:
    def __repr__(self):
        return self.__class__.__name__

    def __eq__(a, b):
        return a.__class__.__name__ == b.__class__.__name__

### NOTE: Cannot solve constraints which needs re-order (e.g. P(y, x), Q(z), R(z, y) should be ordered in Q, R, P)
class Simple(Tactic):
    pass

### NOTE: Cannot use If statements in this tactic
class Simple2(Tactic):
    pass

class WithReorder(Tactic):
    pass