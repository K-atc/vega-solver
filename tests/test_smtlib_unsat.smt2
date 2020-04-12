(set-info :status unknown)
(declare-datatypes () ((Any (a) (b) (c))))
; (declare-fun a () Any)
; (declare-fun b () Any)
; (declare-fun c () Any)
(declare-fun x () Any)
(declare-fun y () Any)
(assert
 (and (= x a) (= y b)))
(assert
 (= x y))
(check-sat)
(get-model)
