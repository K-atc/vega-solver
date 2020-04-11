import sys
from functools import reduce

from .Exceptions import *
from . import AST
from .Law import applyDeMorgansLow
from .Map import RefMap
from .Model import Model
from . import Satisfiability
from .Feature import Feature, FeatureCapability
from . import Tactic
from .smtlib import SmtlibCapability

sat = Satisfiability.Sat()
unsat = Satisfiability.Unsat()
unknown = Satisfiability.Unknown()

class Solver(FeatureCapability, SmtlibCapability):
    def __init__(self, domain, feature=Feature()):
        assert isinstance(domain, AST.Sort)
        assert isinstance(feature, Feature)
        self.domain = domain
        FeatureCapability.__init__(self, feature)

        self.variables = {}
        self.ref = RefMap({})
        self.constraints = []
        self.post_constraints = []
        self.visited_variables = set()

        self.satisfiability = unknown # For optimization
        self.model_start = 0 # For optimization
        self.model_post_start = 0 # For optimization

        # print("Solver.ref = {}".format(self.ref)) # DEBUG
        assert not self.ref # Expect ref is blank

    def declareVariable(self, v):
        assert isinstance(v, AST.Variable)
        if not v in self.variables:
            self.variables[v] = set(self.domain.values)
            ## Exclude values not v.sort holds
            if not v.sort == self.domain:
                self.__addPostConstraint(AST.And(*[AST.Not(AST.Eq(v, t)) for t in self.domain.values - v.sort.values]))

    def add(self, *expr_list):
        for expr in expr_list:
            assert isinstance(expr, AST.AST), "expr={}".format(expr)
            self.constraints.append(expr)
            for v in expr.getVariables():
                self.declareVariable(v)
        self.satisfiability = unknown

    def __addPostConstraint(self, expr):
        assert isinstance(expr, AST.AST)
        self.post_constraints.append(expr)

    def check(self):
        if self.satisfiability == unknown:
            m = self.model()
            if m.sat:
                self.satisfiability = sat
            else:
                self.satisfiability = unsat
        return self.satisfiability

    ### @return Model
    def model(self):
        def __model_constraints(self, debug):
            for i, expr in enumerate(self.constraints[self.model_start:]): # Optimization
                try:
                    if debug and i > 0 and i % 100000 == 0: print("[*] Solver::model(): Solving constraint #{}".format(i)) # DEBUG
                    self.satisfiability = self.__evaluate(expr, self.__and_eq)
                    if debug: assert self.satisfiability == sat
                    if self.satisfiability == unsat:
                        break
                except Exception as e:
                    sys.stdout.flush()
                    print("[X] TheoremSolver::model::__model_constraints(): Exception occured in constraint #{}: {}".format(i, expr))
                    raise e
 
        def __model_post_constraints(self, debug):
            ### Algprithm for reordering problem (P(y, x), Q(z), R(z, y) should solved Q, R, P)
            ### But requires self.visited_variables to manage constrained variables (requied much memory?)
            ### @return sat/unsat
            def __with_reordering_constraints(self, debug):
                visited_variables = self.visited_variables
                unvisited_post_constraints = []
                for i, expr in enumerate(self.post_constraints):
                    try:
                        if not expr.getConditionVariables():
                            self.satisfiability = self.__evaluate_post(expr)
                            if self.satisfiability == unsat:
                                return
                            # visited_variables |= expr.getVariables()
                        else:
                            unvisited_post_constraints.append(expr)
                    except Exception as e:
                        sys.stdout.flush()
                        print("[X] TheoremSolver::model::__model_post_constraints(): Exception occured in post-constraint #{}: {}".format(i, expr))
                        raise e
                
                # print("unvisited_post_constraints = {}".format(unvisited_post_constraints)) # DEBUG
                skip_stop = len(unvisited_post_constraints)
                for i, expr in enumerate(unvisited_post_constraints):
                    try:
                        if debug and i > 0 and i % 100000 == 0: print("[*] Solver::model(): Solving unvisited post-constraint #{}".format(i)) # DEBUG
                        
                        cond_vars = set(map(lambda v: self.ref.getRef(v), expr.getConditionVariables()))
                        # print("cond_vars = {}".format(cond_vars)) # DEBUG
                        # print("visited_variables = {}".format(visited_variables)) # DEBUG

                        ### Give up determing vars in cond_vars from other constraints if i is bigger than length of original unvisited_post_constraints
                        if cond_vars & visited_variables == cond_vars or i >= skip_stop: # intersection
                            self.satisfiability = self.__evaluate_post(expr)
                            if self.satisfiability == unsat:
                                return
                            visited_variables |= set(map(lambda v: self.ref.getRef(v), expr.getVariables()))
                            skip_stop = len(unvisited_post_constraints)
                        else:
                            # print("unvisited_post_constraints: push {}".format(expr)) # DEBUG
                            unvisited_post_constraints.append(expr) # Push to last of iterator
                    except Exception as e:
                        print("[X] TheoremSolver::__model_post_constraints(): Exception occured in expression #{}: {}".format(i, expr))
                        raise e
                return self.satisfiability

            ### @return sat/unsat
            def __simple(self, debug):
                for i, expr in enumerate(self.post_constraints):
                    try:
                        if debug and i > 0 and i % 100000 == 0: print("[*] Solver::model(): Solving post-constraint #{}".format(i)) # DEBUG
                        self.satisfiability = self.__evaluate_post(expr)
                        if debug: assert self.satisfiability == sat
                        if self.satisfiability == unsat:
                            return unsat
                    except Exception as e:
                        print("[X] TheoremSolver::model(): Exception occured in post-constraint #{}: {}".format(i, expr))
                        raise e
                return self.satisfiability

            ### Without reordeing
            if isinstance(self.feature.tactic, Tactic.Simple):
                return __simple(self, debug)

            ### Iterate 2 times to solve reordering problem (but CANNOT support If statements)
            if isinstance(self.feature.tactic, Tactic.Simple2):
                res = __simple(self, debug)
                if res == unsat:
                    return unsat
                else:
                    return __simple(self, debug)
            
            ### With reordering
            if isinstance(self.feature.tactic, Tactic.WithReorder):
                return __with_reordering_constraints(self, debug)
            
            raise UnhandledCaseError("Unhandled tactic = {}".format(self.feature.tactic))
        
        debug = self.feature.debug

        if self.satisfiability == unknown: # Optimization
            ### Process constraints
            __model_constraints(self, debug)

            if self.satisfiability == sat:
                self.model_start = len(self.constraints) # Optimization

                ### NG: produces infinite loop
                # for expr in self.post_constraints:
                #     if expr.getConditionVariables():
                #         unvisited_variables = expr.getVariables() - expr.getConditionVariables()
                #         self.visited_variables -= set(map(lambda v: self.ref.getRef(v), unvisited_variables))

                ### Process post-constraints
                __model_post_constraints(self, debug)

                # if self.satisfiability == sat:
                #     self.model_post_start = len(self.post_constraints) # Optimization
            else:
                if debug: assert False

        return Model(self.satisfiability, self.variables, self.ref)

    def push(self):
        raise ExecutionError('Implement me')

    def pop(self):
        raise ExecutionError('Implement me')
        self.satisfiability = unknown

    def dumpConstraint(self):
        return '\n'.join([str(x) for x in self.constraints])

    def dumpPostConstraint(self):
        return '\n'.join([str(x) for x in self.post_constraints])

    def dumpRefMap(self):
        return self.ref.dump()

    def dumpVariables(self):
        return '\n'.join(['{} = {}'.format(k, v) for k, v in self.variables.items()])

    ### @return: sat or unsat
    def __and_eq(self, left, right):
        # print("[*] __and_eq(left={}, right={})".format(left, right)) # DEBUG
        # print("[*] self.ref.getRef(left) = {}".format(self.ref.getRef(left))) # DEBUG
        assert isinstance(left, AST.Variable)
        assert isinstance(right, AST.Value) or isinstance(right, AST.Variable)
        
        if isinstance(right, AST.Value):
            ref_left = self.ref.getRef(left)
            variables_ref_left = self.variables[ref_left]
            if isinstance(variables_ref_left, set) and not right in variables_ref_left: # Check intersection is not blank
                ### e.g. And(x == {Int}, y == x, y == {Pointer}) is unsat
                # print("[*] __and_eq(left={}, right={}): unsat".format(left, right)) # DEBUG
                # print("[*] __and_eq: variables = {}".format(self.variables)) # DEBUG
                if self.feature.debug: print("[!] __and_eq: symvar Ref({}) = {} cannot be {}".format(left, ref_left, right))
                return unsat
            self.variables[ref_left] = set([right])
            return sat
        
        elif isinstance(right, AST.Variable):
            if left != right: ### NOTE: Dismiss identical assign (i.e. x == x)
                # print("[*] self.variables[left] = AST.Ref(right): left={} right={}".format(left, right)) # DEBUG

                ref_left = self.ref.setRef(left, right)
                variables_left = self.variables[left]

                ### Handle lazy binding (i.e. late y == x)
                if isinstance(variables_left, set) and isinstance(self.variables[ref_left], set):
                    ### i.e. {y |-> {a}} |- {y == a} ~> {x |-> {a}} |- {y == a, y == x}
                    self.variables[ref_left] &= variables_left # intersection

                self.variables[left] = AST.Ref(right)

                if not self.variables[ref_left]: # blank
                    return unsat

            return sat

    ### @return: sat or unsat
    def __or_eq(self, left, right):
        assert isinstance(left, AST.Variable), "type(left)={}".format(type(left))
        assert isinstance(right, AST.Value), "type(right)={}".format(type(right))
        
        self.variables[self.ref.getRef(left)].add(right)
        return sat

    ### @return: sat or unsat
    def __not_eq(self, left, right):
        assert isinstance(left, AST.Variable)
        assert isinstance(right, AST.Value)
        
        ### NOTE: set::remove(key) emits KeyError if set contains key
        ref_left = self.ref.getRef(left)
        variables_ref_left = self.variables[ref_left]
        assert isinstance(variables_ref_left, set), "self.variables[{}] = {}".format(ref_left, variables_ref_left)
        
        if right in variables_ref_left:
            # self.variables[ref_left] &= ref_left.sort.values - set([right]) # intersection
            # self.variables[ref_left] &= self.domain.values - set([right]) # intersection
            self.variables[ref_left].remove(right)
        
        if self.variables[ref_left]:
            return sat
        else:
            if self.feature.debug: raise UnsatException("self.variables[{}] is blank".format(ref_left))
            return unsat

    ### Oneshot side-effect less satisfiability check
    def __check(self, expr):
        if isinstance(expr, AST.Top):
            return sat

        if isinstance(expr, AST.Bot):
            return unsat

        if isinstance(expr, AST.Eq):
            if isinstance(expr.v2, AST.Variable):
                if self.ref.getRef(expr.v1) == self.ref.getRef(expr.v2):
                    return sat
                else:
                    return unsat
            elif isinstance(expr.v2, AST.Value):
                ref_v1 = self.ref.getRef(expr.v1)
                variables_ref_v1 = self.variables[ref_v1]
                assert isinstance(variables_ref_v1, set), "self.variables[{}] = {}".format(ref_v1, variables_ref_v1)
                if expr.v2 in variables_ref_v1:
                    return sat
                else:
                    return unsat
        
        if isinstance(expr, AST.Not):
            if isinstance(expr.v1, AST.Eq):
                if self.__check(expr.v1) == sat:
                    return unsat
                else:
                    return sat

        if isinstance(expr, AST.And):
            return reduce(lambda r, x: r and self.__check(x), expr.v, sat)

        if isinstance(expr, AST.Or):
            return reduce(lambda r, x: r or self.__check(x), expr.v, unsat)
        
        raise UnhandledCaseError("expr: {}".format(expr))

    def __if(self, expr):
        assert isinstance(expr, AST.If)
        
        ### Flip cond clause expression (Remove Not() from cond clause)
        if isinstance(expr.cond_clause, AST.Not):
            return self.__if(AST.If(expr.cond_clause.v1, expr.else_clause, expr.then_clause))

        if self.__check(expr.cond_clause):
            return self.__if_then(expr)
        else:
            return self.__if_else(expr)
        
    def __if_then(self, expr):
        assert isinstance(expr, AST.If)
        res = sat
        ### Assume cond is true
        res &= self.__evaluate(expr.cond_clause, self.__and_eq)
        if self.feature.debug: assert res == sat # DEBUG
        res &= self.__evaluate(expr.then_clause, self.__and_eq)
        if self.feature.debug: assert res == sat # DEBUG
        return res

    def __if_else(self, expr):
        assert isinstance(expr, AST.If)

        if isinstance(expr.else_clause, AST.Terminate):
            return sat

        res = sat
        ### Assume cond is false
        not_cond_expr = applyDeMorgansLow(AST.Not(expr.cond_clause))
        res &= self.__evaluate(not_cond_expr, self.__and_eq)
        if not res == sat: print("[!] Solver::__if_else(expr={}): Not(if-cond) is {}".format(expr, res)) # DEBUG
        res &= self.__evaluate(expr.else_clause, self.__and_eq)
        if self.feature.debug: assert res == sat # DEBUG
        return res

    def __implies(self, expr):
        assert isinstance(expr, AST.Implies)

        if self.__check(expr.left):
            return self.__if_then(AST.If(expr.left, expr.right, AST.Terminate()))
        else:
            return sat

    def __or_on_x(self, expr, x):
        ### Get old type set
        ref_x = self.ref.getRef(x)
        prev_set = self.variables[ref_x] # NOTE: And(x == a, Or(x == b, x == c})) => unsat
        if isinstance(prev_set, AST.Ref):
            # print("[!] prev_set is not type set (potential bug). Assume ref_x is not constrained: prev_set={}, ref.get({})={}".format(prev_set, x, ref_x)) # DEBUG
            prev_set = set(ref_x.sort.values) # Assume prev_set is not constrainted
        
        ### Create new type set
        self.variables[ref_x] = set() # Set blank to collect OR conditions on symvar ref_x
        for v in filter(lambda e: x in e.getVariables(), expr.v):
            res = self.__evaluate(v, self.__or_eq)
            if res == unsat:
                self.variables[ref_x] = prev_set # Restore state for debugging
                if self.feature.debug: raise UnsatException("expression {} produces unsat".format(v))
                return unsat
        
        ### Merge old set and new set
        current_set = self.variables[ref_x]
        update_set = prev_set & current_set # intersection
        # print("[*] Solver::__evaluate(expr={}): ref_x={}, update_set={}".format(expr, ref_x, update_set)) # DEBUG
        
        if update_set:
            self.variables[ref_x] = update_set
            return sat
        else: # Blank
            if self.feature.debug: print("[!] __or_on_x: symvar Ref({}) = {} cannot be any values (prev={}, current={})".format(x, ref_x, prev_set, current_set))
            self.variables[ref_x] = prev_set # Restore state for debugging
            if self.feature.debug: raise UnsatException("variables[{}] is blank".format(ref_x))
            return unsat

    def __eq(self, expr, func):
        if isinstance(expr.v1, AST.Variable):
            if isinstance(expr.v2, AST.Variable) or isinstance(expr.v2, AST.Value):
                return func(expr.v1, expr.v2)
        raise UnhandledCaseError("expr={}".format(expr))

    def __evaluate(self, expr, func):
        # print("[*] __evaluate(expr={}, func={})".format(expr, func.__name__)) # DEBUG
        
        if isinstance(expr, AST.Terminate):
            ### Do nothing
            return sat

        if isinstance(expr, AST.Top):
            return sat

        if isinstance(expr, AST.Bot):
            return unsat
        
        if isinstance(expr, AST.Eq):
            if isinstance(self.feature.tactic, Tactic.WithReorder): self.visited_variables |= set(map(lambda v: self.ref.getRef(v), expr.getVariables()))
            return self.__eq(expr, func)
        
        if isinstance(expr, AST.And):
            if isinstance(self.feature.tactic, Tactic.WithReorder): self.visited_variables |= set(map(lambda v: self.ref.getRef(v), expr.getVariables()))
            return reduce(lambda r, x: r & self.__evaluate(x, self.__and_eq), expr.v, sat)
    
        if isinstance(expr, AST.Or):
            if isinstance(self.feature.tactic, Tactic.WithReorder): self.visited_variables |= set(map(lambda v: self.ref.getRef(v), expr.getVariables()))
            return reduce(lambda r, x: r | self.__or_on_x(expr, x), expr.getVariables(), unsat)
        
        if isinstance(expr, AST.Not):
            if isinstance(self.feature.tactic, Tactic.WithReorder): self.visited_variables |= set(map(lambda v: self.ref.getRef(v), expr.getVariables()))
            if isinstance(expr.v1, AST.Eq): # Not(Eq())
                return self.__eq(expr.v1, self.__not_eq)
            if isinstance(expr.v1, AST.Not): # Not(Not())
                return self.__evaluate(expr.v1.v1, func)
            if isinstance(expr.v1, AST.And) or isinstance(expr.v1, AST.Or): # Not(And()) or Not(Or())
                return self.__evaluate(applyDeMorgansLow(expr), func)

        ### If, Implies are handled in __evaluate_post() (see add())
        if isinstance(expr, AST.If):
            if isinstance(self.feature.tactic, Tactic.Simple2):
                raise ExecutionError("If statement is not supported by tactic {}".format(self.feature.tactic))
            self.__addPostConstraint(expr)
            return sat
        if isinstance(expr, AST.Implies):
            self.__addPostConstraint(expr)
            return sat

        raise UnhandledCaseError('expr: {}'.format(expr))
    
    ### Post phase evaluation
    def __evaluate_post(self, expr):
        if isinstance(expr, AST.If):
            return self.__if(expr)
        if isinstance(expr, AST.Implies):
            return self.__implies(expr)
        return self.__evaluate(expr, self.__and_eq) # Eq() etc.