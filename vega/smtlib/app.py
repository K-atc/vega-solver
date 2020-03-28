from six.moves import cStringIO

from ..Exceptions import *
from .ExtendedSmtLibParser import ExtendedSmtLibParser
from .parse import parse_cmd
from .. import Solver
from ..AST import Sort

def check_sat(expr, sorts):
    ### Calcuate domain
    domain = set()
    for sort in sorts.values():
        domain |= sort.values

    s = Solver(Sort('Domain', domain))
    s.add(*expr)
    return s.check()

def evaluate_smt2_file(file):
    parser = ExtendedSmtLibParser()
    script = parser.get_script(cStringIO(file.read()))

    ### Transform to expressions
    sorts = {}
    expr = []
    for cmd in script:
        if cmd.name in ['declare-datatypes', 'declare-fun', 'assert']:
            res = parse_cmd(cmd, sorts) # NOTE: Do not replace `sorts` with `{}`. `sorts` passes referrence to `sorts`
            if res:
                expr += res
        elif cmd.name in ['check-sat']:
            res = check_sat(expr, sorts)
            print(res)
        elif cmd.name in ['set-info']:
            pass
        else:
            raise UnhandledCaseError("cmd = {}".format(cmd))

