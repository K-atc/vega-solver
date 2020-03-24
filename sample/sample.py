from vega import *

### Define values with name a, b, c, d
a, b, c, d = Value('a'), Value('b'), Value('c'), Value('c')
### Define domain with name Domain
Domain = Sort('Domain', [a, b, c, d])

### Define variables
x = Variable('x', Domain)
y = Variable('y', Domain)
z = Variable('z', Domain)


s = Solver(Domain)
s.add(And(
    Or(
        Eq(x, a),
        Eq(x, b),
        Eq(x, c),
    ),
    Eq(y, x),
    Eq(z, x),
    Not(Eq(z, a)),
))
m = s.model()
print(m)
assert m.sat == sat
print(m[x])