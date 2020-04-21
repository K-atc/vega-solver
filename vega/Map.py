# coding:utf-8

from . import AST
from .Writer import FileWriter, StringWriter

class VariableToVariableMap:
    def __init__(self, values={}):
        assert isinstance(values, dict)
        self.values = values
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.values)

    ### @return AST.Variable
    def __getitem__(self, key):
        assert isinstance(key, AST.Variable)
        return self.values[key]

    def __setitem__(self, key, value):
        assert isinstance(key, AST.Variable), "key={}".format(key)
        assert isinstance(value, AST.Variable), "value={}".format(value)
        self.values[key] = value

    def __delitem__(self, key):
        self.values.__delitem__(key)

    def get(self, key, default):
        assert isinstance(key, AST.Variable), "type(key) = {}".format(type(key))
        assert isinstance(default, AST.Variable), "type(default) = {}".format(type(default))
        return self.values.get(key, default) # use Python built-in dict.get()

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return self.values.__len__()

    def __bool__(self):
        return bool(self.values)

    def dump(self, file=None):
        if file:
            out = FileWriter(file)
        else:
            out = StringWriter()
        if len(self.values) > 0:
            for k, v in self.values.items():
                out.write('{} -> {}'.format(k, v))
            return out.finalize()
        else:
            return '()'


class RefMap(VariableToVariableMap):
    ### @return AST.Variable
    def getRef(self, key, call_count=0):
        # assert isinstance(key, AST.Variable)
        if call_count >= 1000:
            raise Exception("Dropped in infinite loop at Ref({})".format(key))
        
        ref_key = self.get(key, key)
        if key != ref_key:
            res = self.getRef(ref_key, call_count + 1)
            self[ref_key] = res # Memorize result
            return res
        else:
            return key # Fixed point

    ### @return AST.Variable: Ref of child (= `ref[child]`) 
    ### Eq(x, y) |-> x -> y, where x = child and y = Ref(parent)
    def setRef(self, child, parent):
        assert isinstance(child, AST.Variable), "ref: {} -> {}".format(child, parent)
        assert isinstance(parent, AST.Variable), "ref: {} -> {}".format(child, parent)
        
        x = child                       # x
        y = self.getRef(parent)         # y = Ref(parent)
        z = self.getRef(x)              # x'

        ### Assume x is reflective: Ref(x) = x
        if x == z:                      # Do not use too slow `x in self`
            # assert x.name != "File_9_0" or not y.name.startswith("Reg_7ff"), "x={}, y={}".format(x, y) # DEBUG
            self[x] = y                 # x == y
            return y                    # return Ref(x)
        
        ### Redirect relation of (child, parent) since parent is refferenced another child.
        ### Do not check $y != z$ because it calls Variable.__eq__()) and slows execution.
        ### i.e. ∀(x,y,z), {x == y, x == z} ~> {y == z, x == z} (allows x == y or y == z)
        else:
            # assert y.name != "File_9_0" or not z.name.startswith("Reg_7ff"), "y={}, z={}".format(y, z) # DEBUG
            self[y] = z                 # y == z
            return z                    # return Ref(x)
