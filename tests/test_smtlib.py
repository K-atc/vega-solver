from vega import *

expr, domain = parse_smt2_file("study-z3.smt")
print(expr)
print("Domain = {}, Domain.values = {}".format(domain, domain.values))

s = Solver(domain)
s.add(*expr)
m = s.model()
print(m)

for v in m.variables.keys():
    print("{} = {}".format(v, m[v]))