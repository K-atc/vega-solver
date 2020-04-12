from .AST import *

### Check expr a and b are identical (not follows equality of a nor b)
def eq(a, b):
    assert isinstance(a, AST)
    assert isinstance(b, AST)
    return a == b

def is_expr(expr):
    if isinstance(expr, And) or isinstance(expr, Or):
        return expr.v # Assume blank And() is not expression
    else:
        return isinstance(expr, AST)