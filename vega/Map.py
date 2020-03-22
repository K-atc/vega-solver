# coding:utf-8
# from functools import lru_cache

from . import AST

class VariableToVariableMap:
    def __init__(self, values={}):
        # print("[*] VariableToVariableMap::__init__(values={})".format(values)) # DEBUG
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
        # assert key != value # Prohibit identical mapping (i.e. f(x) = x) # TOO SLOW
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

    def dump(self):
        if len(self.values) > 0:
            return '\n'.join(['{} -> {}'.format(k, v) for k, v in self.values.items()])
        else:
            return '()'


class RefMap(VariableToVariableMap):
    ### @return AST.Variable
    # @lru_cache(maxsize=None) # Optimization
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
        # print("[*] RefMap::set(child={}, parent={})".format(child, parent)) # DEBUG
        assert isinstance(child, AST.Variable), "ref: {} -> {}".format(child, parent)
        assert isinstance(parent, AST.Variable), "ref: {} -> {}".format(child, parent)
        
        x = child                       # x
        y = self.getRef(parent)         # y = Ref(parent)
        z = self.getRef(x)              # x'

        # self.getRef.cache_clear()       # Optimization

        ### Assume x is reflective: Ref(x) = x
        if x == z:                      # Do not use too slow `x in self`
            assert x.name != "Reg_7fffe33df877_r10_1683674" or y.name != "File_10_833c" # DEBUG
            self[x] = y                 # x == y
            return y                    # return Ref(x)
        
        ### Redirect relation of (child, parent) since parent is refferenced another child.
        ### Do not check $y != z$ because it calls Variable.__eq__()) and slows execution.
        ### i.e. ∀(x,y,z), {x == y, x == z} ~> {y == z, x == z} (allows x == y or y == z)
        else:
            assert y.name != "Reg_7fffe33df877_r10_1683674" or z.name != "File_10_833c" # DEBUG
            self[y] = z                 # y == z
            return z                    # return Ref(x)
