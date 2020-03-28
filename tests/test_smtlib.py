from vega import *

expr, sorts = parse_smt2_file("study-z3.smt")
print(expr)
print("sorts = {}".format(sorts))

domain = sorts['Any']

s = Solver(domain)
s.add(*expr)
m = s.model()
print(m)

for v in m.variables.keys():
    print("{} = {}".format(v, m[v]))