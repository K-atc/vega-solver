from .SymbolType import SymbolType

class Fnode:
    def __init__(self, name, args):
        self.name = name
        self._args = args

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.name, args)

    def args(self):
        return self._args

    def node_type(self):
        return self.__class__.__name__

    def symbol_name(self):
        return None

    def is_and(self):
        return False
    
    def is_or(self):
        return False
  
    def is_not(self):
        return False
  
    def is_implies(self):
        return False
  
    def is_bool_constant(self):
        return False

    def is_symbol(self):
        return False

    def is_equals(self):
        return False

    def is_ite(self):
        return False

class Blank(Fnode):
    def __init__(self):
        Fnode.__init__(self)

class DataType(Fnode):
    def __init__(self, name, values):
        assert name
        self.name = name
        self.values = values

    def __repr__(self):
        return "{}(name={}, values={})".format(self.__class__.__name__, self.name, self.values)

class And(Fnode):
    def is_and(self):
        return True

class Or(Fnode):
    def is_or(self):
        return True

class Not(Fnode):
    def is_not(self):
        return True

class Implies(Fnode):
    def is_implies(self):
        return True

class BoolConstant(Fnode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)
    
    def constant_value(self):
        return bool(self.name)

    def is_bool_constant(self):
        return True

class Symbol(Fnode):
    def __init__(self, name, _type):
        assert isinstance(_type, SymbolType)
        self.name = name
        self.type = _type

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def symbol_name(self):
        return self.name

    def symbol_type(self):
        return self.type

    def is_symbol(self):
        return True

class Equals(Fnode):
    def is_equals(self):
        return True

class Ite(Fnode):
    def is_ite(self):
        return True