; Test variables defined another sorts
(set-info :status unknown)
(declare-datatypes () ((Domain (a) (b) (c))))
(declare-datatypes () ((D1 (a) (b))))
(declare-datatypes () ((D2 (b) (c))))
; (declare-fun a () Domain)
; (declare-fun b () Domain)
; (declare-fun c () Domain)
(declare-fun x () D1)
(declare-fun y () D2)
(assert
 (or (= x a) (= x c)))
(assert
 (=> (and (distinct x b) true) (= y b)))
(check-sat)
(get-model)
