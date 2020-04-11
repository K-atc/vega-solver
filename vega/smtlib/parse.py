from functools import reduce
from six.moves import cStringIO

from ..Exceptions import *
from ..AST import *
from .pysmt.ExtendedSmtLibParser import ExtendedSmtLibParser
from .vega.VegaSmtLibParser import VegaSmtLibParser

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
        values = [Value(x) for x in cmd.args[0].values]
        sorts[cmd.args[0].name] = Sort(cmd.args[0].name, values)
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
def parse_and_get_script_from_file(file_name):
    with open(file_name) as f:
        return parse_and_get_script_from_file_stream(f)

### @public
def parse_and_get_script_from_file_stream(f):
    # parser = ExtendedSmtLibParser()
    # return parser.get_script(cStringIO(f.read()))

    parser = VegaSmtLibParser()
    return parser.get_script(f.read())

### @public
def parse_smt2_file(file_name):
    script = parse_and_get_script_from_file(file_name)

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