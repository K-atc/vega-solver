from . import AST

### @arg[0] space-separeted names
def Values(names):
    return tuple(map(lambda name: AST.Value, name.split(' ')))