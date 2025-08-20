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

from scipy.spatial import KDTree

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

        self.objects = []
        self.positions = {}
        self.obj_constants = {}
        self.position_constants = {}
        self.predicates = self.parse_predicates_from_domain(domain_name)
        self.init_predicates = []
        self.goal_predicates = []

    def define_init_objects(self, init_config: dict) -> Tuple[List[Constant],
                                                              Dict[str, Constant],
                                                              Dict[str, List[float]],
                                                              Dict[str, Constant]]:
        for obj_name, info in init_config.items():
            obj = Constant(obj_name, type_tag=info["type"])
            self.objects.append(obj)
            self.obj_constants[obj_name] = obj

            pos_name = "p" + str(len(self.positions)+1)
            pos = Constant(pos_name, type_tag="location")
            self.objects.append(pos)

            self.positions[pos_name] = info["position"]
            self.position_constants[pos_name] = pos

        return self.objects, self.obj_constants, self.positions, self.position_constants

    def define_init_predicates(self, obj_constants: Dict[str, Constant],
                                     position_constants: Dict[str, Constant],
                                     predicates: Dict[str, Predicate]) -> List[Predicate]:
        predicates_names = predicates.keys()

        for predicate_name in predicates_names:
            match predicate_name:
                case "gripper-empty":
                    self.init_predicates.extend([predicates["gripper-empty"]()])
                    continue

                case "at":
                    at_predicates = self.define_at_predicates(predicates["at"],
                                                              obj_constants,
                                                              position_constants)
                    self.init_predicates.extend(at_predicates)
                    continue

                case "on":
                    continue

                case "at-top":
                    planar_positions = np.array(list(self.positions.values()))[:, :2]
                    block_tree = KDTree(planar_positions)

                    # TODO: Find a better way to establish physical dependencies between objects
                    for obj_name, obj in obj_constants.items():
                        obj_type = obj_name.split("_")[0]
                        if obj_type == "block":
                            pos_name = "p" + obj_name[-1]
                            pos = self.positions[pos_name]
                            xy_coord = pos[:2]
                            stack = block_tree.query_ball_point(xy_coord, 1)

                            if len(stack) == 1:
                                self.init_predicates.append(predicates["at-top"](obj))
                            else:
                                height = pos[-1]
                                stack_positions = np.array(list(self.positions.values()))[stack]
                                stack_heights = stack_positions[:, -1]
                                if height == max(stack_heights):
                                    self.init_predicates.append(predicates["at-top"](obj))

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
        goal_objs = {}
        goal_pos = {}
        goals = []

        for obj_name, content in goal_config.items():
            obj_constant = self.obj_constants[obj_name]
            goal_objs[obj_name] = obj_constant

            pos = content['position']

            if pos in self.positions.values():
                all_pos_names = list(self.positions.keys())
                pos_index = list(self.positions.values()).index(pos)
                pos_name = all_pos_names[pos_index]
                pos_constant = self.position_constants[pos_name]
            else:
                pos_name = "p" + str(len(self.positions)+1)
                self.positions[pos_name] = pos
                pos_constant = Constant(pos_name, type_tag="location")
                self.position_constants[pos_name] = pos_constant
                self.objects.append(pos_constant)

            goal_pos[pos_name] = pos_constant

        goal_at_predicates = self.define_at_predicates(self.predicates["at"],
                                                       goal_objs,
                                                       goal_pos)

        goals = goal_at_predicates
        goal_conds = goals[0]

        for g in goals[1:]:
            goal_conds = goal_conds & g

        return self.objects, goal_conds

    def define_problem(self, problem_name: str, save: bool = False):
        objects, obj_constants, positions, position_constants = self.define_init_objects(self.init_config)
        init_predicates = self.define_init_predicates(obj_constants, position_constants, self.predicates)
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
                             obj_constants: Dict[str, Constant],
                             pos_constants: Dict[str, Constant]) -> List[Predicate]:

        at_predicates = []
        for obj, pos in zip(obj_constants.values(), pos_constants.values()):
            at_predicates.append(at_predicate(obj, pos))

        return at_predicates

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