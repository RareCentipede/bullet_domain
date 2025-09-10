;Header and description

(define (domain blocks)

    ;remove requirements that are not needed
    (:requirements :typing :negative-preconditions :equality :strips)

    (:types ;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
        location locatable - object
        block agent - locatable
        static dynamic - block
        robot - agent
    )

    ; un-comment following line if constants are needed
    ;(:constants )

    (:predicates ;todo: define predicates here
        (at ?obj - locatable ?loc - location) ; Object ?obj is at location ?loc)
        (on ?block1 - block ?block2 - block)
        (above ?above_loc - location ?below_loc - location)
        (clear ?loc - location)
        (is-ground ?loc - location)
        (at-top ?block - block) ; Block ?block is at the top of its stack
        (gripper-empty)
        (holding ?robot - robot ?block - block) ; Robot ?robot is holding block ?block
        (path-blocked-from-to ?from - location ?to - location) ; Path from ?from to ?to is blocked
    )

    ; (:functions ;todo: define numeric functions here
    ; )

    ;define actions here
    (:action move
            :parameters (?robot - robot
                         ?from - location
                         ?to - location)

            :precondition (and
                (at ?robot ?from)
                (not (path-blocked-from-to ?from ?to)))

            :effect (and
                (not (at ?robot ?from))
                (at ?robot ?to))
    )

    (:action grasp ; Grasp a block from the ground
        :parameters (?robot - robot
                     ?block - dynamic
                     ?loc - location
                     ?gnd - location
        )

        :precondition (and
            (is-ground ?gnd)
            (above ?loc ?gnd)
            (at ?robot ?loc)
            (at ?block ?loc)
            (at-top ?block)
            (gripper-empty)
            (not (holding ?robot ?block))
        )

        :effect (and
            (not (gripper-empty))
            (holding ?robot ?block)

            (not (at ?block ?loc))
            (not (at-top ?block))
            
            (clear ?loc)
        )
    )

    (:action unstack ; Grasp a block from on top of another block
        :parameters (?robot - robot
                     ?block - dynamic
                     ?below_block - block
                     ?loc - location
                     ?below_loc - location
        )

        :precondition (and
            (at ?robot ?loc)
            (gripper-empty)
            (not (holding ?robot ?block))

            (at ?block ?loc)
            (at-top ?block)
            (not (= ?block ?below_block))

            (above ?loc ?below_loc)
            (on ?block ?below_block)
            (at ?below_block ?below_loc)
        )

        :effect (and
            (not (gripper-empty))
            (holding ?robot ?block)

            (not (on ?block ?below_block))
            (not (at ?block ?loc))
            (not (at-top ?block))

            (clear ?loc)
            (at-top ?below_block)
        )
    )

    (:action place ; Place a block on the ground
        :parameters (?robot - robot
                     ?block - dynamic
                     ?loc - location
                     ?gnd - location
        )

        :precondition (and
            (is-ground ?gnd)
            (above ?loc ?gnd)
            (at ?robot ?loc)
            (holding ?robot ?block)
            (clear ?loc)
        )

        :effect (and
            (not (holding ?robot ?block))
            (gripper-empty)
            (at ?block ?loc)
            (not (clear ?loc))
            (at-top ?block)
        )
    )

    (:action stack
        :parameters (?robot - robot
                     ?block - dynamic
                     ?below_block - block
                     ?loc - location
                     ?below_loc - location
        )

        :precondition (and 
            (at ?robot ?loc)
            (holding ?robot ?block)

            (not (is-ground ?below_loc))
            (not (= ?loc ?below_loc))
            (clear ?loc)
            (above ?loc ?below_loc)

            (not (= ?block ?below_block))
            (at ?below_block ?below_loc)
            (at-top ?below_block)
        )

        :effect (and
            (gripper-empty)
            (not (holding ?robot ?block))
            (not (clear ?loc))

            (at ?block ?loc)
            (at-top ?block)
            (on ?block ?below_block)

            (not (at-top ?below_block))
        )
    )
)