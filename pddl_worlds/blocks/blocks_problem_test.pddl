(define (problem test) (:domain blocks)
(:objects
    block_1 - static
    block_2 block_3 block_4 block_5 - dynamic
    p1 p2 p3 p4 p5 p7 p6 p8 pr pt - location
    larry - robot
)

(:init
    ;todo: put the initial state's facts and numeric values here
    (at block_1 p1)
    (at block_2 p2)
    (at block_3 p3)
    (at block_4 p4)
    (at block_5 p5)

    (occupied p1)
    (occupied p2)
    (occupied p3)
    (occupied p4)
    (occupied p5)

    (on block_5 block_4)
    (on block_3 block_2)

    (at-top block_1)
    (at-top block_3)
    (at-top block_5)

    (above p5 p4)
    (above p3 p2)
    (above p6 p5)
    (above p7 p1)
    (above p8 p3)

    (valid-location p1)
    (valid-location p2)
    (valid-location p3)
    (valid-location p4)
    (valid-location p5)
    (valid-location p6)
    (valid-location p7)
    (valid-location p8)

    (gripper-empty)

    (at larry pr)
    
)

(:goal (and
    ;todo: put the goal condition here
    (at block_5 p1)
    (at block_4 p1)
    (at block_3 p1)
    (at block_2 p1)

    (on block_5 block_4)
    (on block_4 block_3)
    (on block_3 block_2)
    (on block_2 block_1)
))

;un-comment the following line if metric is needed
;(:metric minimize (???))
)