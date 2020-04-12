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
