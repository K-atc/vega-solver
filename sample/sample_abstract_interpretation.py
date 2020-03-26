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

"""
 76e:	48 8d 05 cb 08 20 00 	lea    rax,[rip+0x2008cb]
 775:	48 01 d0             	add    rax,rdx
"""

s = Solver(Any)

s.add(lea(Reg('76e_rax'), Reg('76e_rip')))

s.add(add(Reg('775_rax'), Reg('775_rdx')))
s.add(Eq(Reg('775_rax'), Reg('76e_rax')))

m = s.model()
print(m[Reg('775_rdx')])