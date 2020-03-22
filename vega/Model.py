# coding:utf-8
from . import AST
from .Map import RefMap
from .Satisfiability import Satisfiability, Sat

class Model(dict):
    def __init__(self, sat, variables, ref):
        assert isinstance(sat, Satisfiability)
        assert isinstance(ref, RefMap)
        assert isinstance(variables, dict) # Map Variable -> set を型にしたい
        self.sat = sat
        self.ref = ref
        self.variables = {} # ダンプを簡単にするために専用dictを用意して使いたい
        for key, value in variables.items():
            self.variables[key] = value

    def __repr__(self):
        if len(self.variables) < 100:
            return "{}(sat={}, {})".format(self.__class__.__name__, self.sat, self.variables)
        else: # Avoid too long output
            return "{}(sat={}, ...)".format(self.__class__.__name__, self.sat)
    
    def __getitem__(self, key):
        ref_key = self.ref.getRef(key)
        if ref_key in self.variables:
            return self.variables[ref_key]
        else:
            return None

    def __setitem__(self, key, value):
        # print("[*] Model::__setitem__(key={}, value={})".format(key, value)) # DEBUG
        assert isinstance(value, set) or isinstance(value, AST.Ref) # 専用の型を用意したい
        self.variables[self.ref.getRef(key)] = value

    def __bool__(self):
        return isinstance(self.sat, Sat)