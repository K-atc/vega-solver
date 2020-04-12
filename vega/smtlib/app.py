from six.moves import cStringIO

from ..Exceptions import *
from .parse import parse_cmd, parse_and_get_script_from_file_stream
from ..Solver import Solver, sat, unsat, unknown
from ..AST import Sort
from ..Tactic import Simple2

def calcuate_domain(sorts):
    domain = set()
    for sort in sorts.values():
        domain |= sort.values
    return Sort('Domain', domain)

def check_sat(expr, s, profile):
    s.add(*expr)
    res = s.check()
    print(res)

    if profile:
        s.profileMemoryUsage()

    return res

def get_model(s):
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

def error_model_is_not_avaiable(cmd_no):
    print('(error "command #{}: model is not available")'.format(cmd_no))
    exit(1)

def evaluate_smt2_file(file, profile):
    script = parse_and_get_script_from_file_stream(file)

    ### Evaluate script
    sorts = {}
    expr = []
    solver = None
    sat = unknown
    for cmd_no, cmd in enumerate(script):
        if cmd.name in ['declare-datatypes', 'declare-fun', 'assert']:
            res = parse_cmd(cmd, sorts) # NOTE: Do not replace `sorts` with `{}`. `sorts` passes referrence to `sorts`
            if res:
                expr += res
        elif cmd.name in ['check-sat']:
            ### Initialize solver
            Domain = calcuate_domain(sorts)
            solver = Solver(Domain, tactic=Simple2())

            sat = check_sat(expr, solver, profile)
        elif cmd.name in ['get-model']:
            if not solver:
                error_model_is_not_avaiable(cmd_no)
            sat = get_model(solver)
        elif cmd.name in ['set-info']:
            pass
        else:
            raise UnhandledCaseError("cmd = {}".format(cmd))

        if sat == unsat:
            error_model_is_not_avaiable(cmd_no)