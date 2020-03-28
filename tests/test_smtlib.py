import argparse
from vega import *

parser = argparse.ArgumentParser(description='parse input smt file and transform to output smt file')
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

expr, domain = parse_smt2_file(args.input)
print(expr)
print("Domain = {}, Domain.values = {}".format(domain, domain.values))

s = Solver(domain)
s.add(*expr)
m = s.model()
print(m)

for v in m.variables.keys():
    print("{} = {}".format(v, m[v]))

with open(args.output, "w") as f:
    f.write(s.to_smt2())