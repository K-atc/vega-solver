from .AST import *

### Check expr a and b are identical (not follows equality of a nor b)
def eq(a, b):
    assert isinstance(a, AST)
    assert isinstance(b, AST)
    return a == b

def is_expr(expr):
    return isinstance(expr, AST)