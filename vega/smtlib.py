from functools import reduce
from six.moves import cStringIO
from collections import namedtuple

from pysmt.smtlib.parser import SmtLibParser
from pysmt.smtlib.script import SmtLibCommand
from pysmt.typing import PySMTType

from .Exceptions import *
from .AST import *

DataType = namedtuple('DataType', ['name', 'values'])

class ExtendedSmtLibParser(SmtLibParser):
    def __init__(self, env=None, interactive=False):
        SmtLibParser.__init__(self, env, interactive)

        self.commands["declare-datatypes"] = self._cmd_declare_datatypes
        self.commands["declare-fun"] = self._cmd_declare_fun

    def _parse_declare_datatypes(self, tokens):
        closing_clause_depth = 0
        parsed_tokens = []
        while True:
            tk = tokens.consume()
            parsed_tokens.append(tk)
            if tk == '(':
                closing_clause_depth += 1
            elif tk == ')':
                closing_clause_depth -= 1
            if closing_clause_depth == -1:
                break
        return parsed_tokens

    def _cmd_declare_datatypes(self, current, tokens):
        expr = self._parse_declare_datatypes(tokens)
        expr = list(filter(lambda x: not x in ['(', ')'], expr))
        ### Register variable for `declare-fun`
        self.cache.bind(expr[0], self._get_var(expr[0], PySMTType(basename=expr[0])))
        return SmtLibCommand(name="declare-datatypes", args=DataType(expr[0], expr[1:]))

    ### Overwrite definition of _cmd_declare_fun()
    def _cmd_declare_fun(self, current, tokens):
        """(declare-fun <symbol> (<sort>*) <sort>)"""
        var = self.parse_atom(tokens, current)
        params = self.parse_params(tokens, current)
        typename = self.parse_type(tokens, current)
        self.consume_closing(tokens, current)

        if params:
            typename = self.env.type_manager.FunctionType(typename, params)

        ### Cast FNode to PySMTType
        ### This fixes bug of original `_cmd_declare_fun`)
        typename = PySMTType(basename=typename.symbol_name())

        v = self._get_var(var, typename)
        if v.symbol_type().is_function_type():
            self.cache.bind(var, \
                    functools.partial(self._function_call_helper, v))
        else:
            self.cache.bind(var, v)
        return SmtLibCommand(current, [v])

sorts = {}

def parse_fnode(fnode, depth=1):
    if fnode.is_and():
        res = []
        for x in fnode.args():
            res.append(parse_fnode(x))
        return And(*res)
        # return And(*reduce(lambda r, x: r.append(parse_fnode(x)), fnode.args(), []))
    
    elif fnode.is_or():
        res = []
        for x in fnode.args():
            res.append(parse_fnode(x))
        return Or(*res)
        # return Or(*reduce(lambda r, x: r.append(parse_fnode(x)), fnode.args(), []))
    
    elif fnode.is_not():
        return Not(parse_fnode(fnode.args()[0]))
    
    elif fnode.is_implies():
        return Implies(
            parse_fnode(fnode.args()[0]), 
            parse_fnode(fnode.args()[1])
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
        return Eq(parse_fnode(fnode.args()[0]), parse_fnode(fnode.args()[1]))
    
    elif fnode.is_ite():
        return If(parse_fnode(fnode.args()[0]), parse_fnode(fnode.args()[1]), parse_fnode(fnode.args()[2]))
    else:
        raise UnhandledCaseError("{}: node_type = {}".format(fnode, fnode.node_type()))

def parse_cmd(cmd):
    if cmd.name == 'declare-datatypes':
        values = [Value(x) for x in cmd.args.values]
        sorts[cmd.args.name] = Sort(cmd.args.name, values)
        return []
    
    if cmd.name == 'declare-fun':
        symbol_name = cmd.args[0].symbol_name()
        sort_name = cmd.args[0].symbol_type().name
        return []
    
    if cmd.name == 'assert':
        res = []
        for x in cmd.args:
            res.append(parse_fnode(x))
        return res
        # return reduce(lambda r, x: r.append(parse_fnode(x)), cmd.args, [])

### @public
def parse_smt2_file(file_name):
    with open(file_name) as f:
        parser = ExtendedSmtLibParser()
        script = parser.get_script(cStringIO(f.read()))

        ### Transform to expressions
        expr = []
        for cmd in script:
            res = parse_cmd(cmd)
            if res:
                expr += res

        ### Calcuate domain
        domain = set()
        for sort in sorts.values():
            domain |= sort.values

        return expr, Sort('Domain', domain)

class SmtlibCapability:
    ### serialize constraints
    def to_smt2(self):
        res = []
        for expr in self.constraints + self.post_constraints:
            res.append(expr.to_smt2())
        return '\n'.join(res)