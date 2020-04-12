vega: All Sat Style Theorem Solver
====


<img src="./vega_logo_with_letter_LOGO_PORTRAIT.png" width="120pt"/>

*vega* is yet another theorem solver and answers all values which satisfies given constraints on each variable as a model (in sat solver, this behavior is called as all sat solver).

For example, if there're variable x ∈ {a,b,c} and constraints x = a ∧ x ≠ c, vega's solution is x = {a,b}. This means x is a or b. Note that general SMT solver's (such as z3) solution x = a does not covers all satisfiable values and such solvers requires much more time to obtain another solution.

See [white paper](./White-Paper-of-vega.pdf) to find out detailed technical background.


Requirements
----
* Python3
* Pypy3 (Optional)
    * Recommend use Pypy3 to speed up execution


Remarks
----
* vega is implemented as pypi library 
* vega has similar API to z3py. (see demo)
* vega provides command line tool `vega` similar to `z3` (see demo)


How to setup
----
All you have to do is pip install `vega-solver`.

```shell
pip3 install vega-solver
```


How to test
----
|CI test status|
|:-:|
|![Python test](https://github.com/K-atc/vega-solver/workflows/Python%20test/badge.svg)|

You can test if vega works correctly using bundled test scripts. 
Clone this repository and run test commands in `.github/workflows/pythontest.yml`.


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
a, b, c, d = Value('a'), Value('b'), Value('c'), Value('d')
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
Model(sat=sat, {z: Ref(x), y: Ref(x), x: {c, b}})
{c, b}
```

We found that vega models that *x* is *b* or *c* and this is correct solution for this constraint.

See [test.py](../tests/test.py) for more examples.

### Abstract Interpretation
Abstract interpretation is a analysis method to obtation information about targetted computer program's semantics.
In this method, a program is executed using abstracted values not concrete values. 

This PoC performs abstract interpretation on 3 types (*Int*, *Pointer*, *PointerOffset*) and reasons that type of register `rdx` is not *Int* in following asembly code.

```assembly
 76e:	48 8d 05 cb 08 20 00 	lea    rax,[rip+0x2008cb]
 775:	48 01 d0             	add    rax,rdx
```

in `sample/sample_abstract_interpretation.py`:

```python
from vega import *

Int, Pointer, PointerOffset = Value('Int'), Value('Pointer'), Value('PointerOffset')
Any = Sort('Any', [Int, Pointer, PointerOffset])

def symvar(name):
    return Variable(name, Any)

def Reg(name):
    return symvar("Reg_{}".format(name))

def add(dst, src):
    return Implies(
        Not(Eq(dst, Int)),
        Not(Eq(src, Int))
    )

def lea(dst, base):
    return And(
        Not(Eq(dst, Int)),
        Not(Eq(base, Int)),
    )


s = Solver(Any)

s.add(lea(Reg('76e_rax'), Reg('76e_rip')))

s.add(add(Reg('775_rax'), Reg('775_rdx')))
s.add(Eq(Reg('775_rax'), Reg('76e_rax')))

m = s.model()
print(m[Reg('775_rdx')])
```

Note that this solver:

* assumes type of dst is not *Int* on each `lea` instruction, and
* assumes type of src is not *Int* if type of dst is not *Int* on each `add` instruction.

Execution result:

```
$ python3 sample/sample_abstract_interpretation.py 
{Pointer, PointerOffset}
```

### SMT-LIB support
vega has [SMT-LIB language](http://smtlib.cs.uiowa.edu/language.shtml) support as z3 do. SMT-LIB language is oriented for SMT solver and describes formulas.

Command usage is similar to z3.

```
$ cat tests/test_smtlib_1.smt2
(set-info :status unknown)
(declare-datatypes () ((Any (a) (b) (c))))
; (declare-fun a () Any)
; (declare-fun b () Any)
; (declare-fun c () Any)
(declare-fun x () Any)
(declare-fun y () Any)
(assert
 (or (= x a) (= x c)))
(assert
 (=> (and (distinct x b) true) (= y b)))
(check-sat)
(get-model)

$ vega -smt2 tests/test_smtlib_1.smt2
sat
(model
  (define-fun x () Any
    (as (or a c) Any))
  (define-fun y () Any
    (as b Any))
)
```

In case of z3:

```
$ z3 -smt2 tests/test_smtlib_1.smt2
sat
(model
  (define-fun y () Any
    b)
  (define-fun x () Any
    a)
)
```

### Performance benchmark
`sample/gzip.-l.trace.constraint.smt2` contains:
* 397784 assertions
* 935725 variables (number of `declare-fun`)

File size of this smt2 is 110 MB.

vega (installed by pypy3) solves this large constraints in 41 seconds and requires 2.4 GB memory. 
Note that vega solves given constraint at `(check-sat)`.

```
$ /usr/bin/time -v vega -smt2 sample/gzip.-l.trace.constraint.smt2
sat
        Command being timed: "vega -smt2 sample/gzip.-l.trace.constraint.smt2"
        User time (seconds): 38.58
        System time (seconds): 2.62
        Percent of CPU this job got: 99%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:41.21
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 2390212
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 884111
        Voluntary context switches: 5
        Involuntary context switches: 138
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0
```

In case of z3:

```
$ (cat sample/gzip.-l.trace.constraint.smt2; echo "(get-model)") | /usr/bin/time -v z3 -in | tail
Command exited with non-zero status 1
        Command being timed: "z3 -in"
        User time (seconds): 65.77
        System time (seconds): 1.15
        Percent of CPU this job got: 99%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 1:06.94
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 847480
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 297452
        Voluntary context switches: 2
        Involuntary context switches: 1239
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 1
    (as Int Any))
  (define-fun Mem_7ffff7de1c98_555555556798_573717 () Any
    (as Int Any))
  (define-fun Mem_7ffff7de19d8_5555555565d8_497565 () Any
    (as Int Any))
  (define-fun Mem_7ffff7de19d8_5555555561d1_312496 () Any
    (as Int Any))
  (define-fun Mem_7ffff7de19d8_555555556338_373436 () Any
    (as Int Any))
)
```

We found that vega is faster than z3, but requires much memory.