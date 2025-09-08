import numpy as np

from abc import abstractmethod
from pddl.logic import Predicate, constants, variables, Variable, Constant
from pddl.core import Domain, Problem, Formula
from pddl.action import Action
from pddl.requirements import Requirements
from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem

from yaml import safe_load
from typing import Dict, List, Union, Tuple
from dataclasses import dataclass

from scipy.spatial import KDTree

problem_config_path = "config/problem_configs/"

@dataclass 
class PositionObject:
    name: str
    pos: List[float]
    constant: Constant
    occupied_by: Union["Object", None] = None

@dataclass
class Object:
    name: str
    type_tag: str
    constant: Constant
    pos: PositionObject
    predicates: List[Predicate]

class PddlProblemParser:
    def __init__(self, config_name: str,
                       domain_name: str,
                       problem_config_path: str = "config/problem_configs/") -> None:
        
        self.init_path = f"{problem_config_path}{config_name}/init.yaml"
        self.goal_path = f"{problem_config_path}{config_name}/goal.yaml"
        self.domain_name = domain_name

        with open(self.init_path, 'r') as f:
            self.init_config = safe_load(f)
            f.close()

        with open(self.goal_path, 'r') as f:
            self.goal_config = safe_load(f)
            f.close()

        self.things = []
        self.objects = {}
        self.positions = {}

        self.init_predicates = []
        self.goal_predicates = []
        self.predicates = self.parse_predicates_from_domain(domain_name)

    def define_init_objects(self, init_config: dict) -> Tuple[Dict[str, Object], Dict[str, PositionObject]]:
        for obj_name, info in init_config.items():
            obj = Constant(obj_name, type_tag=info["type"])

            pos_name = "p" + str(len(self.positions)+1)
            pos = Constant(pos_name, type_tag="location")

            self.things.append(obj)
            self.things.append(pos)

            pos_class = PositionObject(name=pos_name,
                                       pos=info["position"],
                                       constant=pos)

            obj_class = Object(name=obj_name,
                               type_tag=info["type"],
                               constant=obj,
                               pos=pos_class,
                               predicates=[])

            pos_class.occupied_by = obj_class

            self.positions[pos_name] = pos_class
            self.objects[obj_name] = obj_class

        return self.objects, self.positions

    def define_init_predicates(self, objects: Dict[str, Object],
                                     positions: Dict[str, PositionObject],
                                     predicates: Dict[str, Predicate]) -> List[Predicate]:
        predicates_names = predicates.keys()
        stacks = find_stacks(self.positions)

        for predicate_name in predicates_names:
            match predicate_name:
                case "gripper-empty":
                    self.init_predicates.extend([predicates["gripper-empty"]()])
                    continue

                case "at":
                    object_list = list(objects.values())
                    position_list = list(positions.values())
                    at_predicates = self.define_at_predicates(predicates["at"], object_list, position_list)
                    self.init_predicates.extend(at_predicates)
                    continue

                case "on":
                    for stack in stacks:
                        if len(stack) == 1:
                            continue

                        # Order the positions in the stack by their z value
                        pos_objs = [self.positions[p] for p in stack]
                        sorted_pos = sorted(pos_objs, key=lambda x: x.pos[2], reverse=True)

                        for i in range(len(sorted_pos)-1):
                            lower_pos = sorted_pos[i+1]
                            upper_pos = sorted_pos[i]

                            lower_obj = lower_pos.occupied_by
                            upper_obj = upper_pos.occupied_by

                            on_predicate = predicates["on"](upper_obj.constant, lower_obj.constant)
                            self.init_predicates.append(on_predicate)

                    continue

                case "at-top":
                    at_top_predicates = self.define_at_top_predicates(predicates["at-top"], stacks, self.positions)
                    self.init_predicates.extend(at_top_predicates)
                    continue

                case "path-blocked-from-to":
                    continue

                case "holding":
                    continue

                case _:
                    print(f"Predicate {predicate_name} not implemented")
                    raise NotImplementedError()

        return self.init_predicates

    def define_goal_conditions(self, goal_config: Dict) -> Tuple[List[Constant], Union[Predicate, Formula]]:
        goal_objs = []
        goal_pos = []
        goals = []

        for obj_name, content in goal_config.items():
            obj = self.objects[obj_name]
            goal_objs.append(obj)

            pos = content['position']
            pos_name = find_pos_id_from_value(self.positions, pos)

            if pos_name is not None:
                pos_obj = self.positions[pos_name]
            else:
                pos_name = "p" + str(len(self.positions)+1)
                pos_constant = Constant(pos_name, type_tag="location")
                pos_obj = PositionObject(name=pos_name,
                                         pos=pos,
                                         constant=pos_constant)
                self.positions[pos_name] = pos_obj
                self.things.append(pos_constant)

            goal_pos.append(pos_obj)

        goal_at_predicates = self.define_at_predicates(self.predicates["at"], goal_objs, goal_pos)

        stacks = find_stacks(self.positions)
        goal_on_predicates = self.define_on_predicates(self.predicates["on"], stacks, self.positions)

        goals = goal_at_predicates + goal_on_predicates
        goal_conds = goals[0]

        for g in goals[1:]:
            goal_conds = goal_conds & g

        return self.things, goal_conds

    def define_problem(self, problem_name: str, save: bool = False):
        objects, positions = self.define_init_objects(self.init_config)
        init_predicates = self.define_init_predicates(objects, positions, self.predicates)
        objects, goal_conds = self.define_goal_conditions(self.goal_config)

        problem = Problem(name=problem_name,
                          domain_name=self.domain_name,
                          objects=objects,
                          init=init_predicates,
                          goal=goal_conds)

        print(f"Problem defined successfully: {problem}")

        if save:
            with open(f"pddl_worlds/{self.domain_name}/{problem_name}.pddl", "w") as f:
                f.write(problem_to_string(problem))
                f.close()

        return problem

    @staticmethod
    def parse_predicates_from_domain(world_name: str) -> Dict[str, Predicate]:
        domain_path = f"pddl_worlds/{world_name}/{world_name}_domain.pddl"

        # Domain expansion!!!
        domain = parse_domain(domain_path)
        predicates_list = list(domain.predicates)
        predicates = {}

        for p in predicates_list:
            p_name = p.name
            predicates[p_name] = p

        return predicates

    @staticmethod
    def define_at_predicates(at_predicate: Predicate,
                             objects: List[Object],
                             positions: List[PositionObject]) -> List[Predicate]:

        at_predicates = []
        for obj, pos in zip(objects, positions):
            at_predicates.append(at_predicate(obj.constant, pos.constant))

            # Update position occupancy
            old_pos = obj.pos
            old_pos.occupied_by = None

            pos.occupied_by = obj # type: ignore
            obj.pos = pos

        return at_predicates

    @staticmethod
    def define_at_top_predicates(at_top_predicate: Predicate,
                                 stacks: List[List[str]],
                                 positions: Dict[str, PositionObject]) -> List[Predicate]:
        at_top_predicates = []
        for stack in stacks:
            if len(stack) == 1:
                top_obj = positions[stack[0]].occupied_by
            else:
                pos_objs = [positions[p] for p in stack]
                top_pos_id = np.argmax([p.pos[2] for p in pos_objs])
                top_pos = pos_objs[top_pos_id]
                top_obj = top_pos.occupied_by

            if top_obj is not None:
                at_top_predicates.append(at_top_predicate(top_obj.constant))

        return at_top_predicates

    @staticmethod
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

def parse_plan(plan_file: str) -> List[Tuple[str, List[str]]]:
    cmd_book = []
    with open(plan_file, 'r') as f:
        plan = f.readlines()

    for i in range(len(plan)-1):
        plan[i] = plan[i].strip()
        plan[i] = plan[i][1:-1]
        cmd_line = plan[i].split(' ')
        cmd = cmd_line[0]
        args = cmd_line[1:]

        cmd_book.append([cmd, args])

    return cmd_book

def find_pos_id_from_value(positions: Dict[str, PositionObject], pos: List[float]) -> Union[str, None]:
    pos_names = positions.keys()
    pos_coords = [p.pos for p in positions.values()]

    if pos not in pos_coords:
        return None

    pos_indx = pos_coords.index(pos)
    pos_id = list(pos_names)[pos_indx]

    return pos_id

def find_stacks(positions: Dict[str, PositionObject], threshold: float = 0.5) -> List[List[str]]:
    stacks = []
    visited_ids = []

    # Make KDTree for the positions
    pos_objs = positions.values()
    pos_names = positions.keys()

    pos_coords = [p.pos for p in pos_objs]
    planar_positions = np.array(pos_coords)[:, :2]
    block_tree = KDTree(planar_positions)

    # One of the positions is for the robot, which cannot be part of any block stack
    i = 0
    while len(visited_ids) < (len(pos_names)-1):
        if i in visited_ids:
            i += 1
            continue

        pos_coord = pos_coords[i]

        stack_inds = block_tree.query_ball_point(pos_coord[:2], threshold)

        if stack_inds == []:
            stacks.append([list(pos_names)[i]])
            i += 1
            continue

        pos_in_stack = np.array(list(pos_names))[stack_inds]
        stacks.append(pos_in_stack.tolist())
        visited_ids.extend(list(stack_inds))

        i += 1

    return stacks