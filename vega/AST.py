from functools import reduce

def checkAllItemsAreAST(*z):
    return reduce(lambda r, x: r and (isinstance(x, AST)), z, True)

def checkAllItemsAreValue(*z):
    return reduce(lambda r, x: r and (isinstance(x, Value)), z, True)

class AST:
    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def describe(self):
        return self.__repr__()

    def __hash__(self):
        return hash(self.__repr__())

    def getVariables(self):
        return set()

    def getConditionVariables(self, is_parent_condition=False):
        return set()

class Variable(AST):
    def __init__(self, name, sort):
        assert isinstance(name, str)
        assert isinstance(sort, Sort)
        self.name = name
        self.sort = sort

    def __repr__(self):
        return self.name
        # return self.describe()

    def describe(self):
        return "{}(name={}, sort={})".format(self.__class__.__name__, self.name, self.sort)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(a, b):
        return a.name == b.name # and a.sort == b.sort

    def getVariables(self):
        return set([self])

    def getConditionVariables(self, is_parent_condition=False):
        if is_parent_condition:
            return self.getVariables()
        else:
            return set()

class Sort(AST):
    def __init__(self, name, values):
        assert isinstance(name, str)
        assert isinstance(values, set) or isinstance(values, list)
        assert checkAllItemsAreValue(*values)
        self.name = name
        self.values = set(values)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def __eq__(a, b):
        return a.name == b.name and a.values == b.values

class Value(AST):
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name

    def __repr__(self):
        return self.name

    def describe(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(a, b):
        return a.name == b.name

### Used to describe equality x == y |-> x = Ref(y)
class Ref(AST):
    def __init__(self, var):
        assert isinstance(var, Variable)
        self.variable = var
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.variable)

    def __eq__(a, b):
        return  a.__class__.__name__ == b.__class__.__name__ and a.variable == b.variable

class Const(AST):
    def __init__(self):
        pass

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def __eq__(a, b):
        return a.__class__.__name__ == b.__class__.__name__

    def getVariables(self):
        return set()

class NOp(AST):
    def __init__(self, *v):
        assert checkAllItemsAreAST(*v), "v={}".format(v)
        self.v = list(v)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(['{}'.format(x) for x in self.v]))

    def __eq__(a, b):
        return a.v == b.v

    def getVariables(self):
        return reduce(lambda r, expr: r | expr.getVariables(), self.v, set())

    def getConditionVariables(self, is_parent_condition=False):
        return reduce(lambda r, expr: r | expr.getConditionVariables(is_parent_condition), self.v, set())

class UniOp(NOp):
    def __init__(self, v1):
        assert isinstance(v1, AST)
        self.v1 = v1
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.v1)

    def __eq__(a, b):
        return a.v1 == b.v1

    def getVariables(self):
        return self.v1.getVariables()

    def getConditionVariables(self, is_parent_condition=False):
        return self.v1.getConditionVariables(is_parent_condition)

class BinOp(NOp):
    def __init__(self, v1, v2):
        assert isinstance(v1, AST)
        assert isinstance(v2, AST)
        self.v1 = v1
        self.v2 = v2
    
    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.v1, self.v2)

    def __eq__(a, b):
        return a.v1 == b.v1 and a.v2 == b.v2

    def getVariables(self):
        # res = set()
        # if isinstance(self.v1, Variable):
        #     res.add(self.v1)
        # elif isinstance(self.v1, NOp):
        #     res |= self.v1.getVariables()
        # if isinstance(self.v2, Variable):
        #     res.add(self.v2)
        # elif isinstance(self.v2, NOp):
        #     res |= self.v2.getVariables()
        # return res
        return self.v1.getVariables() | self.v2.getVariables()

    def getConditionVariables(self, is_parent_condition=False):
        return self.v1.getConditionVariables(is_parent_condition) | self.v2.getConditionVariables(is_parent_condition)

### Holds no AST nodes
class Terminate(Const):
    pass

### True
class Top(Const):
    pass

### False
class Bot(Const):
    pass

class Not(UniOp):
    pass

class Eq(BinOp):
    pass

class And(NOp):
    pass

class Or(NOp):
    pass

class If(AST):
    def __init__(self, cond_clause, then_clause, else_clause):
        assert isinstance(cond_clause, AST)
        assert isinstance(then_clause, AST)
        assert isinstance(else_clause, AST)
        self.cond_clause = cond_clause
        self.then_clause = then_clause
        self.else_clause = else_clause

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, self.cond_clause, self.then_clause, self.else_clause)

    def getVariables(self):
        return self.cond_clause.getVariables() | self.then_clause.getVariables() | self.else_clause.getVariables()

    def getConditionVariables(self, is_parent_condition=False):
        return self.cond_clause.getConditionVariables(True)

class Implies(AST):
    def __init__(self, left, right):
        assert isinstance(left, AST)
        assert isinstance(right, AST)
        self.left = left
        self.right = right

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.left, self.right)

    def getVariables(self):
        return self.left.getVariables() | self.right.getVariables()

    def getConditionVariables(self, is_parent_condition=False):
        return self.left.getConditionVariables(True)