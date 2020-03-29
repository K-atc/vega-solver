import unittest

from vega import *

Int, Pointer, PointerOffset = Value('Int'), Value('Pointer'), Value('PointerOffset')
Any = Sort('Any', [Int, Pointer, PointerOffset])
S = Sort('Int', [Int])

x = Variable('x', Any)
y = Variable('y', Any)
z = Variable('z', Any)
w = Variable('w', S)


class TestGlobalFunctions(unittest.TestCase):
    def test_eq(self):
        print("\n[*] eq()")
        self.assertEqual(eq(Not(Eq(x, Int)), Not(Eq(x, Int))), True)
        self.assertEqual(eq(Or(Eq(x, Int), Eq(y, Int)), Or(Eq(x, Int), Eq(y, Int))), True)

    def test_is_expr(self):
        print("\n[*] is_expr()")
        self.assertEqual(is_expr(Or(x, y)), True)
        self.assertEqual(is_expr(x), True)
        self.assertEqual(is_expr(1), False)


class TestNotAndOr(unittest.TestCase):
    def test_Not(self):
        print("\n[*] x != Int")
        s = Solver(Any)
        s.add(Not(Eq(x, Int)))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], Any.values - set([Int]))

    def test_And_Or(self):
        print("\n[*] And(Or(x == Int, x == PointerOffset), y == Int)")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Int),
                Eq(x, PointerOffset),
            ),
            Eq(y, Int),
        ))
        m = s.model()
        print(m)
        print("ref: {}".format(s.ref))
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int, PointerOffset]))
        self.assertEqual(m[y], set([Int]))

    def test_join_Or_Or(self):
        print("\n[*] x == {Pointer, PointerOffset}, x == {Int, PointerOffset}")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Pointer),
                Eq(x, PointerOffset),
            ),
            Or(
                Eq(x, Int),
                Eq(x, PointerOffset),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([PointerOffset]))

    def test_Or_with_multi_variables(self):
        print("\n[*] Test Or() contains multiple variables: x == Int, y == Pointer, Or(x != Int, y == Pointer)")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            Eq(y, Pointer),
            Or(
                Not(Eq(x, Int)),
                Eq(y, Pointer),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Pointer]))

    def test_de_morgans_law_Not_Or(self):
        print("\n[*] Test de morgan's law: Not(Or(x != Int, y != Int))")
        s = Solver(Any)
        s.add(Not(
            Or(
                Not(Eq(x, Int)),
                Not(Eq(y, Int)),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Int]))

    def test_de_morgans_law_Not_And(self):
        print("\n[*] Test de morgan's law: Not(And(x != Int, x != Pointer, y != Int))")
        s = Solver(Any)
        s.add(Not(
            And(
                Not(Eq(x, Int)),
                Not(Eq(x, Pointer)),
                Not(Eq(y, Int)),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int, Pointer]))
        self.assertEqual(m[y], set([Int]))


class TestEquality(unittest.TestCase):
    def test_potential_infinite_loop(self):
        print("\n[*] And(x == Int, y == x, y == y)")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            Eq(y, x),
            Eq(y, y), # NOTE: reflective ref
            ))
        m = s.model()
        print(m)
        print("ref: {}".format(s.ref))
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Int]))

    def test_equality_sigle_hop(self):
        print("\n[*] And(x == Int, y == x)")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            Eq(y, x),
        ))
        m = s.model()
        print(m)
        print("s.variables = {}".format(s.variables))
        print("ref: {}".format(s.ref))
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[y], set([Int]))

    def test_equality_multi_hop(self):
        print("\n[*] And(Or(x == Pointer, x == PointerOffset), y == x, z == x, z == Pointer)")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Pointer),
                Eq(x, PointerOffset),
            ),
            Eq(y, x),
            Eq(z, x),
            Eq(z, Pointer),
        ))
        m = s.model()
        print(m)
        print("ref: {}".format(s.ref))
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Pointer]))
        self.assertEqual(m[y], set([Pointer]))
        self.assertEqual(m[z], set([Pointer]))

    def test_lazy_binding(self):
        print("\n[*] And(Or(z == Int), y == x, z == y)")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(z, Int),
            ),
            Eq(y, x),
            Eq(z, y),
        ))
        m = s.model()
        print(m)
        print("ref: {}".format(s.ref))
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Int]))
        self.assertEqual(m[z], set([Int]))

    def test_double_parent_problem(self):
        print("\n[*] Test double parent node: x == y, x == z, x = {Int}")
        s = Solver(Any)
        s.add(And(
            Eq(x, y),
            Eq(x, z),
            Eq(x, Int),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Int]))
        self.assertEqual(m[z], set([Int]))

    def test_double_parent_problem_with_potential_looped_edges(self):
        print("\n[*] Test double parent node (potential looped edges pattern): x == z, y == z, x == y, x = {Int}")
        s = Solver(Any)
        s.add(And(
            Eq(x, z),
            Eq(y, z),
            Eq(x, Int),
            Eq(x, y),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Int]))
        self.assertEqual(m[z], set([Int]))

    def test_join_another_sort(self):
        print("\n[*] Test Eq join with another sort: y == x, y == w")
        s = Solver(Any)
        s.declareVariable(x)
        s.declareVariable(y)
        s.declareVariable(w)
        s.add(And(
            Eq(y, x),
            Eq(y, w),
        ))
        m = s.model()
        print(m)
        print("constraints = {}".format(s.constraints))
        print("post_constraints = {}".format(s.post_constraints))
        print("ref = {}".format(s.ref))
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set(w.sort.values))
        self.assertEqual(m[y], set(w.sort.values))
        self.assertEqual(m[w], set(w.sort.values))


class TestUnsat(unittest.TestCase):
    def test_P_and_not_P(self):
        print("\n[*] And(x == Int, x != Int)")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            Not(Eq(x, Int)),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, unsat)

    def test_no_model(self):
        print("\n[*] Test unsat: x == {Pointer, PointerOffset}, x == {Int}")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Pointer),
                Eq(x, PointerOffset),
            ),
            Or(
                Eq(x, Int),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, unsat)

    def test_contradiction(self):
        print("\n[*] test contradiction: x == {Int}, y == {Pointer}, x == y")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            Eq(y, Pointer),
            Eq(x, y)
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, unsat)

class TestIfStatement(unittest.TestCase):
    def test_if_then(self):
        print("\n[*] Test if-then: x == {Pointer, PointerOffset}, If(x == Pointer, y == {Int}, y == {Pointer})")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Pointer),
                Eq(x, PointerOffset),
            ),
            If(
                Eq(x, Pointer),
                Eq(y, Int),
                Eq(y, Pointer),
            ),
        ))
        m = s.model()
        print(m)
        print("post_constraints = {}".format(s.post_constraints))
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Pointer]))
        self.assertEqual(m[y], set([Int]))

    def test_if_else(self):
        print("\n[*] Test if-else: x == {Pointer, PointerOffset}, If(x == Int, y == {Int}, y == {Pointer})")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Pointer),
                Eq(x, PointerOffset),
            ),
            If(
                Eq(x, Int),
                Eq(y, Int),
                Eq(y, Pointer),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Pointer, PointerOffset]))
        self.assertEqual(m[y], set([Pointer]))

    def test_if_else_with_not_in_condition(self):
        print("\n[*] Test if-else: x == {Pointer, PointerOffset}, If(x != Pointer, y == {Int}, y == {Pointer})")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Pointer),
                Eq(x, PointerOffset),
            ),
            If(
                Not(Eq(x, Pointer)),
                Eq(y, Int),
                Eq(y, Pointer),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Pointer]))
        self.assertEqual(m[y], set([Pointer]))

    def test_if_then_and_And_in_condition(self):
        print("\n[*] Test if-then and And() in if-cond: x == Int, y == Pointer, If(And(x == Int, y != Int), z == y, z == y)")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            Eq(y, Pointer),
            If(
                And(
                    Eq(x, Int),
                    Not(Eq(y, Int)),
                ),
                Eq(z, y),
                Eq(z, y),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Pointer]))

    def test_if_then_and_Or_in_condition(self):
        print("\n[*] Test if-then: x == Int, If(Or(x == Int, x == Pointer), y == {Int}, y == {Pointer})")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            If(
                Or(
                    Eq(x, Int),
                    Eq(x, Pointer),
                ),
                Eq(y, Int),
                Eq(y, Pointer),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Int]))

    def test_de_morgans_law(self):
        print("\n[*] Test de morgan's law: Test if-else and And() in if-cond: x == Int, y == Pointer, If(And(x == Int, y != Pointer), z == y, z == y)")
        s = Solver(Any)
        s.add(And(
            Eq(x, Int),
            Eq(y, Pointer),
            If(
                And(
                    Eq(x, Int),
                    Not(Eq(y, Pointer)),
                ),
                Eq(z, y),
                Eq(z, y),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Int]))
        self.assertEqual(m[y], set([Pointer]))


class TestImpliesStatement(unittest.TestCase):
    def test_Implies(self):
        print("\n[*] Test implies statement: x == {Pointer, PointerOffset}, Implies(x == Pointer, y == {Int})")
        s = Solver(Any)
        s.add(And(
            Or(
                Eq(x, Pointer),
                Eq(x, PointerOffset),
            ),
            Implies(
                Eq(x, Pointer),
                Eq(y, Int),
            ),
        ))
        m = s.model()
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], set([Pointer]))
        self.assertEqual(m[y], set([Int]))

    def test_only_Implies(self):
        print("\n[*] Implies(x == Int, y == Int), Implies(x != Int, y == Int)")
        s = Solver(Any)
        s.add(Implies(
            Eq(x, Int),
            Eq(y, Int),
        ))
        m = s.model()
        print(m)
        assert m.sat
        assert m[x] == set([Int])


class TestPloblemOfReorderingConstraints(unittest.TestCase):
    def test_reorder_PQR(self):
        print("\n[*] P(y, x), Q(z), R(z, y)")
        s = Solver(Any)
        s.add(Implies(
            Not(Eq(y, Int)),
            Not(Eq(x, Int)),
        )) # P(y, x)
        s.add(Not(Eq(z, Int))) # Q(z)
        s.add(Implies(
            Not(Eq(z, Int)),
            Not(Eq(y, Int)),
        )) # R(z, y)
        m = s.model() # Solve with order Q, R, P
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], x.sort.values - set([Int]))
        self.assertEqual(m[y], y.sort.values - set([Int]))
        self.assertEqual(m[z], z.sort.values - set([Int]))

    def test_reorder_PQQR(self):
        print("\n[*] Test re-order constraints: P(y, x), Q(z), Q'(y), R(z, y)")
        s = Solver(Any, Feature(tactic=Tactic.Simple2())) # Cannot solve tightly with default tactic WithReorder (which solves with order Q, Q', P, R)
        s.add(Implies(
            Not(Eq(y, Pointer)),
            Not(Eq(x, Int)),
        )) # P(y, x)
        s.add(Not(Eq(z, Int))) # Q(z)
        s.add(Not(Eq(y, Int))) # Q'(y)
        s.add(Implies(
            Not(Eq(z, Int)),
            Not(Eq(y, Pointer)),
        )) # R(z, y)
        m = s.model() # Solve with order Q, Q', R, P
        print(m)
        self.assertEqual(m.sat, sat)
        self.assertEqual(m[x], x.sort.values - set([Int]))
        self.assertEqual(m[y], y.sort.values - set([Int, Pointer]))
        self.assertEqual(m[z], z.sort.values - set([Int]))

    ### TODO
    # def test_potential_unsat(self):
    #     print("\n[*] Test potential unsat: Implies(P(x), Q(y)), Implies(R(y), Not(P(x)) where R(y) = true")
    #     # s = Solver(Any, Feature(tactic=Tactic.WithReorder()))
    #     s = Solver(Any)
    #     s.add(Implies(
    #         Eq(x, Int),
    #         Eq(y, Int),
    #     ))
    #     s.add(Implies(
    #         Or(
    #             Eq(y, Int),
    #             Eq(y, Pointer),
    #         ),
    #         Not(Eq(x, Int)),
    #     ))
    #     m = s.model() # First right clause of Implies() shold not be evalueated
    #     print(m)
    #     self.assertEqual(m.sat, sat, msg=m)
    #     self.assertEqual(m[x], x.sort.values - set([Int]))
    #     self.assertEqual(m[y], set([Int, Pointer]))

if __name__ == "__main__":
    unittest.main()