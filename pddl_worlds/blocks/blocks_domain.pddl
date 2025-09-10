;Header and description

(define (domain blocks)

    ;remove requirements that are not needed
    (:requirements :typing :negative-preconditions :conditional-effects :disjunctive-preconditions :existential-preconditions)

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
        (above ?loc1 - location ?loc2 - location) ; Location ?loc1 is above location ?loc2
        (occupied ?loc - location) ; Location ?loc is occupied by some block
        (valid-location ?loc - location) ; Location ?loc is a valid location
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
                    (forall (?below_block - block)
                        (when (on ?block ?below_block)
                            (at-top ?below_block)
                        )
                    )
                    (not (occupied ?loc))
                    (forall (?above_loc - location)
                        (when (above ?above_loc ?loc)
                            (not (valid-location ?above_loc))
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
                        (not (occupied ?loc))
                        (valid-location ?loc)
                      )

        :effect (and
                    (gripper-empty)
                    (not (holding ?robot ?block))
                    (at ?block ?loc)
                    (occupied ?loc)
                    (forall (?above_loc - location)
                        (when (above ?above_loc ?loc)
                            (and
                                (valid-location ?above_loc)
                                (not (occupied ?above_loc))       
                            )
                        )
                    )
                    (forall (?below_loc - location)
                        (when (above ?loc ?below_loc)
                            (forall (?below_block - block)
                                (when (at ?below_block ?below_loc)
                                    (and 
                                        (not (at-top ?below_block))
                                        (on ?block ?below_block)    
                                    )
                                )
                            )
                        )
                    )
                    (at-top ?block)
                )
    )
)