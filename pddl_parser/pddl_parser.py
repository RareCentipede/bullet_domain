import numpy as np

from pddl.logic import Predicate, Constant
from pddl.core import Problem, Formula
from pddl.formatter import problem_to_string
from pddl import parse_domain

from yaml import safe_load
from typing import Dict, List, Union, Tuple
from dataclasses import replace

from scipy.spatial import KDTree
from pddl_parser.predicate_definitions import *

problem_config_path = "config/problem_configs/"

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
        self.ground = Constant("gnd", type_tag="location")
        self.things.append(self.ground)

    def define_init_objects(self, init_config: dict) -> Tuple[Dict[str, Object], Dict[str, PositionObject]]:
        for obj_name, info in init_config.items():
            obj = Constant(obj_name, type_tag=info["type"])

            pos_name = "p" + str(len(self.positions)+1)
            pos = Constant(pos_name, type_tag="location")

            self.things.append(obj)
            self.things.append(pos)

            pos_class = PositionObject(name=pos_name, pos=info["position"], constant=pos)
            obj_class = Object(name=obj_name, type_tag=info["type"], constant=obj, pos=pos_class, predicates=[])

            pos_class.occupied_by = obj_class

            self.positions[pos_name] = pos_class
            self.objects[obj_name] = obj_class

        return self.objects, self.positions

    def define_goal_objects(self, goal_config: Dict) -> Tuple[List[Object], Dict[str, PositionObject], Dict[str, PositionObject]]:
        goal_objs_list = []
        goal_pos_dict = self.positions.copy()

        for obj_name, content in goal_config.items():
            obj = replace(self.objects[obj_name])

            pos = content['position']
            pos_name = find_pos_id_from_value(self.positions, pos)

            # If position is already in the dictionary, just grab it
            # Otherwise, make a new Constant and PositionObject
            if pos_name is not None:
                pos_obj = goal_pos_dict[pos_name]
            else:
                pos_name = "p" + str(len(self.positions)+1)
                pos_constant = Constant(pos_name, type_tag="location")
                pos_obj = PositionObject(name=pos_name,
                                         pos=pos,
                                         constant=pos_constant)
                self.positions[pos_name] = replace(pos_obj)
                goal_pos_dict[pos_name] = pos_obj

                # Only new positions have to be added to the 'thing' list
                # New positions should always be free at the beginning
                self.things.append(pos_constant)

            goal_pos = pos_obj
            goal_pos.occupied_by = obj
            obj.pos = goal_pos

            goal_pos_dict[pos_name] = goal_pos
            goal_objs_list.append(obj)

        return goal_objs_list, goal_pos_dict, self.positions

    def define_init_predicates(self, objects: Dict[str, Object],
                                     positions: Dict[str, PositionObject],
                                     predicates: Dict[str, Predicate]) -> List[Predicate]:
        predicates_names = list(predicates.keys())

        stacks = find_stacks(self.positions)

        for predicate_name in predicates_names:
            match predicate_name:
                case "gripper-empty":
                    self.init_predicates.extend([predicates["gripper-empty"]()])
                    continue

                case "at":
                    object_list = list(objects.values())
                    at_predicates = define_at_predicates(predicates["at"], object_list)
                    self.init_predicates.extend(at_predicates)
                    continue

                case "on":
                    on_predicates = define_on_predicates(predicates["on"], stacks, positions)
                    self.init_predicates.extend(on_predicates)
                    continue

                case "at-top":
                    at_top_predicates = define_at_top_predicates(predicates["at-top"], stacks, positions)
                    self.init_predicates.extend(at_top_predicates)
                    continue

                case "clear":
                    clear_predicate = predicates["clear"]
                    clear_predicates = define_clear_predicates(clear_predicate, positions)
                    self.init_predicates.extend(clear_predicates)
                    continue

                case "is-ground":
                    ground_predicate = predicates["is-ground"](self.ground)
                    self.init_predicates.append(ground_predicate)
                    continue

                case "above":
                    above_predicates = define_above_predicates(predicates["above"], stacks, positions, self.ground)
                    self.init_predicates.extend(above_predicates)
                    continue

                case "path-blocked-from-to":
                    continue

                case "holding":
                    continue

                case _:
                    print(f"Predicate {predicate_name} not implemented")
                    raise NotImplementedError()

        return self.init_predicates

    def define_goal_conditions(self, goal_objs: List[Object], positions: Dict[str, PositionObject]) -> Tuple[List[Constant], Union[Predicate, Formula]]:
        stacks = find_stacks(positions)

        goal_at_predicates = define_at_predicates(self.predicates["at"], goal_objs)
        goal_on_predicates = define_on_predicates(self.predicates["on"], stacks, positions)

        goals = goal_at_predicates + goal_on_predicates
        goal_conds = goals[0]

        for g in goals[1:]:
            goal_conds = goal_conds & g

        return self.things, goal_conds

    def define_problem(self, problem_name: str, save: bool = False):
        objects, positions = self.define_init_objects(self.init_config)
        goal_objs_list, goal_pos_dict, positions = self.define_goal_objects(self.goal_config)

        init_predicates = self.define_init_predicates(objects, positions, self.predicates)
        objects, goal_conds = self.define_goal_conditions(goal_objs_list, goal_pos_dict)

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