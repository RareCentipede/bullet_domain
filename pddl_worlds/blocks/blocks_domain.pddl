;Header and description

(define (domain blocks)

    ;remove requirements that are not needed
    (:requirements :adl :negative-preconditions :existential-preconditions)

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
        (at-top ?block - block) ; Block ?block is at the top of its stack
        (gripper-empty)
        (holding ?robot - robot ?block - block) ; Robot ?robot is holding block ?block
        (path-blocked-from-to ?from - location ?to - location) ; Path from ?from to ?to is blocked
        (is-ground ?loc - location)
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

    (:action grasp
        :parameters (?robot - robot
                     ?block - dynamic
                     ?loc - location
                     ?pos - location
        )

        :precondition (and
                        (at ?robot ?loc)
                        (at ?block ?loc)
                        (at ?block ?pos)
                        (gripper-empty)
                        (at-top ?block)
                      )

        :effect (and
                    (not (at ?block ?loc))
                    (not (at ?block ?pos))
                    (holding ?robot ?block)
                    (not (gripper-empty))
                    (forall (?below_block - block)
                        (when (on ?block ?below_block)
                            (and
                                (at-top ?below_block)
                                (not (on ?block ?below_block))
                            )
                        )
                    )
                )
    )

    (:action place
        :parameters (?robot - robot
                     ?block - dynamic
                     ?loc - location
                     ?pos - location
        )

        :precondition (and
                        (at ?robot ?loc)
                        (holding ?robot ?block)
                        (not (gripper-empty))
                      )

        :effect (and
                    (gripper-empty)
                    (not (holding ?robot ?block))
                    (at ?block ?loc)
                    (at-top ?block)
                )
    )
)