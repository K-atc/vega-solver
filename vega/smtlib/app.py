from six.moves import cStringIO

from ..Exceptions import *
from .parse import parse_cmd, parse_and_get_script_from_file_stream
from ..Solver import Solver, sat, unsat, unknown
from ..AST import Sort

def calcuate_domain(sorts):
    domain = set()
    for sort in sorts.values():
        domain |= sort.values
    return Sort('Domain', domain)

def check_sat(expr, sorts):
    Domain = calcuate_domain(sorts)
    s = Solver(Domain)
    s.add(*expr)
    res = s.check()
    print(res)
    return res

def get_model(expr, sorts):
    Domain = calcuate_domain(sorts)
    s = Solver(Domain)
    s.add(*expr)
    m = s.model()
    if m.sat == sat:
        print("(model")
        for v in m.variables.keys():
            if len(m[v]) > 1:
                ans = "(or {})".format(' '.join([x.name for x in m[v]]))
            else:
                ans = list(m[v])[0].name
            print("  (define-fun {name} () {sort_name}\n    (as {ans} {sort_name}))".format(name=v, sort_name=v.sort.name, ans=ans))
        print(")")
    return m.sat

def evaluate_smt2_file(file):
    script = parse_and_get_script_from_file_stream(file)

    ### Transform to expressions
    sorts = {}
    expr = []
    sat = unknown
    for line_no, cmd in enumerate(script):
        if cmd.name in ['declare-datatypes', 'declare-fun', 'assert']:
            res = parse_cmd(cmd, sorts) # NOTE: Do not replace `sorts` with `{}`. `sorts` passes referrence to `sorts`
            if res:
                expr += res
        elif cmd.name in ['check-sat']:
            sat = check_sat(expr, sorts)
        elif cmd.name in ['get-model']:
            sat = get_model(expr, sorts)
        elif cmd.name in ['set-info']:
            pass
        else:
            raise UnhandledCaseError("cmd = {}".format(cmd))

        if sat == unsat:
            print('(error "command #{}: model is not available")'.format(line_no))
            exit(1)