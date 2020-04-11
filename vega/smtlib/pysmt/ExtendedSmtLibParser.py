from functools import reduce
from six.moves import cStringIO
from collections import namedtuple

from pysmt.smtlib.parser import SmtLibParser
from pysmt.smtlib.script import SmtLibCommand
from pysmt.typing import PySMTType

from ...Exceptions import *

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
        # for x in expr:
        #     self.cache.bind(x, self._get_var(x, PySMTType(basename=x)))
        return SmtLibCommand(name="declare-datatypes", args=[DataType(expr[0], expr[1:])])

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