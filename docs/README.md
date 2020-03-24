vega: Theorem Solver To Find All Satisfiable Values
====

![Python test](https://github.com/K-atc/vega-solver/workflows/Python%20test/badge.svg)

![](logo.png) TODO: Add Logo

*vega* is yet another theorem solver and answers all values which satisfies given constraints on each variable as a model (in sat solver, this behavior is called as all sat solver).

For example, if there're variable x ∈ {a,b,c} and constraints x = a ∧ x ≠ c, vega's solution is x = {a,b}. This means x is a or b. Note that general SMT solver's (such as z3) solution x = a does not covers all satisfiable values and such solvers requires much more time to obtain another solution.

See [white paper](./White-Paper-of-vega.pdf) to find out detailed technical background.


Remarks
----
- vega has similar API to z3py.


How to setup
----
```shell
pip3 install vega-solver
```


Test
----
You can test if vega works correctly using bundled test scripts. 

Clone this repository and run:

```shell
python3 -m tests.test
```


Demo
----
### Simple equations
In this demo, we check following points:

* Does vega handles equality of variables *a, b, c* correcly?
* Does vega reasons a model satisfies given constraint?

`sample/sample.py`:

```python
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
```

Execution result:

```
$ python3 sample/sample.py 
Model(sat=Sat, {x: {c, b}, y: Ref(x), z: Ref(x)})
{b, c}
```

We found that vega models *x* to be *b* or *c* and this is correct answer for this constraint.

See [test.py](../tests/test.py) for more examples.

### Abstract Interpretation
TBD