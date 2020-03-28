from functools import reduce
from six.moves import cStringIO

from ..Exceptions import *
from ..AST import *
from .ExtendedSmtLibParser import ExtendedSmtLibParser

def parse_fnode(fnode, sorts, depth=1):
    if fnode.is_and():
        res = []
        for x in fnode.args():
            res.append(parse_fnode(x, sorts))
        return And(*res)
        # return And(*reduce(lambda r, x: r.append(parse_fnode(x)), fnode.args(), []))
    
    elif fnode.is_or():
        res = []
        for x in fnode.args():
            res.append(parse_fnode(x, sorts))
        return Or(*res)
        # return Or(*reduce(lambda r, x: r.append(parse_fnode(x)), fnode.args(), []))
    
    elif fnode.is_not():
        return Not(parse_fnode(fnode.args()[0], sorts))
    
    elif fnode.is_implies():
        return Implies(
            parse_fnode(fnode.args()[0], sorts), 
            parse_fnode(fnode.args()[1], sorts)
            )
    
    elif fnode.is_symbol():
        symbol_name = fnode.symbol_name()
        sort_name = fnode.symbol_type().name
        if Value(symbol_name) in sorts[sort_name].values: # Check if symbol is member of datatype
            return Value(symbol_name)
        else:
            return Variable(symbol_name, sorts[sort_name])
    
    elif fnode.is_bool_constant():
        value = fnode.constant_value() # -> <class 'bool'>
        if value:
            return Top()
        else:
            return Bot()
    
    elif fnode.is_equals():
        return Eq(parse_fnode(fnode.args()[0], sorts), parse_fnode(fnode.args()[1], sorts))
    
    elif fnode.is_ite():
        return If(parse_fnode(fnode.args()[0], sorts), parse_fnode(fnode.args()[1], sorts), parse_fnode(fnode.args()[2], sorts))
    else:
        raise UnhandledCaseError("{}: node_type = {}".format(fnode, fnode.node_type()))

def parse_cmd(cmd, sorts):
    if cmd.name == 'declare-datatypes':
        values = [Value(x) for x in cmd.args.values]
        sorts[cmd.args.name] = Sort(cmd.args.name, values)
        return []
    
    if cmd.name == 'declare-fun':
        # symbol_name = cmd.args[0].symbol_name()
        # sort_name = cmd.args[0].symbol_type().name
        return []
    
    if cmd.name == 'assert':
        res = []
        for x in cmd.args:
            res.append(parse_fnode(x, sorts))
        return res
        # return reduce(lambda r, x: r.append(parse_fnode(x)), cmd.args, [])

### @public
def parse_smt2_file(file_name):
    with open(file_name) as f:
        parser = ExtendedSmtLibParser()
        script = parser.get_script(cStringIO(f.read()))

        ### Transform to expressions
        sorts = {}
        expr = []
        for cmd in script:
            res = parse_cmd(cmd, sorts) # NOTE: Do not replace `sorts` with `{}`. `sorts` passes referrence to `sorts`
            if res:
                expr += res

        ### Calcuate domain
        domain = set()
        for sort in sorts.values():
            domain |= sort.values

        return expr, Sort('Domain', domain)