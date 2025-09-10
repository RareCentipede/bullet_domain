(define (problem test) (:domain blocks)
(:objects
    block_1 - static
    block_2 block_3 block_4 block_5 - dynamic
    p1 p2 p3 p4 p5 p7 p6 p8 p9 p10 p11 p12 p13 p14 p15 p16 pr pt ground - location
    larry - robot
)

(:init
    ;todo: put the initial state's facts and numeric values here
    (is-ground ground)

    (at block_1 p1)
    (at-top block_1)
    (above p1 ground)

    (at block_5 p5)
    (at block_4 p4)
    (on block_5 block_4)
    (above p5 p4)
    (above p4 ground)
    (at-top block_5)

    (at block_3 p3)
    (at block_2 p2)
    (on block_3 block_2)
    (above p3 p2)
    (above p2 ground)
    (at-top block_3)

    (above p9 p1)
    (above p8 p9)
    (above p7 p8)
    (above p6 p7)
    (clear p9)
    (clear p8)
    (clear p7)
    (clear p6)
    
    (gripper-empty)

    (at larry pr)

    (above p10 ground)
    (above p11 ground)
    (above p12 ground)
    (above p13 ground)
    (above p14 ground)
    (above p15 ground)
    (above p16 ground)

    (clear ground)
    (clear p10)
    (clear p11)
    (clear p12)
    (clear p13)
    (clear p14)
    (clear p15)
    (clear p16)
)

(:goal (and
    ;todo: put the goal condition here
    (at block_5 p6)
    (at block_4 p7)
    (at block_3 p8)
    (at block_2 p9)

    (at-top block_5)
    (on block_5 block_4)
    (on block_4 block_3)
    (on block_3 block_2)
    (on block_2 block_1)
))

;un-comment the following line if metric is needed
;(:metric minimize (???))
)