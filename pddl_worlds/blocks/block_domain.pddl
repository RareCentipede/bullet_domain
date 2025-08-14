;Header and description

(define (domain block_world)

    ;remove requirements that are not needed
    (:requirements :typing :negative-preconditions :conditional-effects)

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
    )

    (:functions ;todo: define numeric functions here
    )

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
                     ?loc - location)

        :precondition (and
                        (at ?robot ?loc)
                        (at ?block ?loc)
                        (gripper-empty)
                        (at-top ?block)
                      )

        :effect (and
                    (not (at ?block ?loc))
                    (holding ?robot ?block)
                    (not (gripper-empty))
                    (not (at-top ?block))
                    (forall (?below_block - block)
                        (when (on ?block ?below_block)
                            (at-top ?below_block)
                        )
                    )
                )
    )

    (:action place
        :parameters (?robot - robot
                     ?block - dynamic
                     ?loc - location)

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
                    (forall (?below_block - block)
                        (when (and
                                (at ?below_block ?loc)
                                (at-top ?below_block)
                              )
                            (and
                                (not (at-top ?below_block))
                                (on ?block ?below_block)
                            )
                        )
                    )
                )

    )
)