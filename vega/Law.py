from .AST import *

def applyDeMorgansLow(expr):
    # print("[*] applyDeMorgansLow(expr={})".format(expr)) # DEBUG
    assert isinstance(expr, Not)
    assert isinstance(expr.v1, Eq) or isinstance(expr.v1, And) or isinstance(expr.v1, Or)

    if isinstance(expr.v1, Eq):
        return expr
    if isinstance(expr.v1, And):
        return Or(*[Not(e) for e in expr.v1.v])
    if isinstance(expr.v1, Or):
        return And(*[Not(e) for e in expr.v1.v])
    