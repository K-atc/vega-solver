; benchmark generated from python API
(set-info :status unknown)
(declare-datatypes () ((Any (Variable) (Pointer) (UInt))))
(declare-fun Variable () Any)
(declare-fun Pointer () Any)
(declare-fun UInt () Any)
(declare-fun x () Any)
(declare-fun y () Any)
(assert
 (or (= x Variable) (= x UInt)))
(assert
 (=> (and (distinct x Pointer) true) (= y Pointer)))
(check-sat)