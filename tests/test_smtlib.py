import argparse
from vega import *

parser = argparse.ArgumentParser(description='parse input smt file and transform to output smt file')
parser.add_argument("input")
parser.add_argument("output", nargs='?')
args = parser.parse_args()

if args.output:
    prefix = ""
else:
    prefix = "; "

expr, domain = parse_smt2_file(args.input)
print("{}{}".format(prefix, expr))
print("{}Domain = {}, Domain.values = {}".format(prefix, domain, domain.values))

s = Solver(domain)
s.add(*expr)
m = s.model()
print("{}{}".format(prefix, m))

for v in m.variables.keys():
    print("{}{} = {}".format(prefix, v, m[v]))

if args.output:
    with open(args.output, "w") as f:
        f.write(s.to_smt2())
else:
    print(s.to_smt2())