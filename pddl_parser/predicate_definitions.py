import numpy as np
from pddl.logic import Predicate, Constant

from typing import Dict, List
from pddl_parser.pddl_parser import Object, PositionObject

def define_at_predicates(at_predicate: Predicate, objects: List[Object]) -> List[Predicate]:

    at_predicates = []
    for obj in objects:
        at_predicates.append(at_predicate(obj.constant, obj.pos.constant))

    return at_predicates

def define_at_top_predicates(at_top_predicate: Predicate,
                                stacks: List[List[str]],
                                positions: Dict[str, PositionObject]) -> List[Predicate]:
    at_top_predicates = []
    for stack in stacks:
        pos_objs = [positions[p] for p in stack]

        occupied_positions = [p for p in pos_objs if p.occupied_by is not None]

        if occupied_positions == []:
            continue

        top_pos_id = np.argmax([p.pos[2] for p in occupied_positions])
        top_pos = pos_objs[top_pos_id]
        top_obj = top_pos.occupied_by

        at_top_predicates.append(at_top_predicate(top_obj.constant)) # type: ignore

    return at_top_predicates

def define_on_predicates(on_predicate: Predicate,
                            stacks: List[List[str]],
                            positions: Dict[str, PositionObject]) -> List[Predicate]:
    on_predicates = []
    for stack in stacks:
        if len(stack) == 1:
            continue

        # Order the positions in the stack by their z value
        pos_objs = [positions[p] for p in stack]
        sorted_pos = sorted(pos_objs, key=lambda x: x.pos[2], reverse=True)

        for i in range(len(sorted_pos)-1):
            lower_pos = sorted_pos[i+1]
            upper_pos = sorted_pos[i]

            lower_obj = lower_pos.occupied_by
            upper_obj = upper_pos.occupied_by

            if lower_obj is not None and upper_obj is not None:
                on_predicates.append(on_predicate(upper_obj.constant, lower_obj.constant))

    return on_predicates

def define_above_predicates(above_predicate: Predicate,
                            stacks: List[List[str]],
                            positions: Dict[str, PositionObject],
                            ground: Constant) -> List[Predicate]:
    above_predicates = []
    for stack in stacks:
        if len(stack) == 1:
            above_gnd_pos = positions[stack[0]].constant
            above_p = above_predicate(above_gnd_pos, ground)
            above_predicates.append(above_p)
            continue

        # Order the positions in the stack by their z value
        pos_objs = [positions[p] for p in stack]
        sorted_pos = sorted(pos_objs, key=lambda x: x.pos[2], reverse=True)
        above_gnd_pos = sorted_pos[-1].constant
        above_p = above_predicate(above_gnd_pos, ground)
        above_predicates.append(above_p)

        for i in range(len(sorted_pos)-1):
            lower_pos = sorted_pos[i+1]
            upper_pos = sorted_pos[i]

            above_predicates.append(above_predicate(upper_pos.constant, lower_pos.constant))

    return above_predicates

def define_clear_predicates(clear_predicate: Predicate,
                            positions: Dict[str, PositionObject]) -> List[Predicate]:
    clear_predicates = []

    for pos_obj in positions.values():
        if pos_obj.occupied_by is None:
            clear_predicates.append(clear_predicate(pos_obj.constant))

    return clear_predicates