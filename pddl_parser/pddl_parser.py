from abc import abstractmethod
from pddl.logic import Predicate, constants, variables, Variable, Constant
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.requirements import Requirements
from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem

from yaml import safe_load
from typing import Dict, List, Union, Tuple

from operator import itemgetter

problem_config_path = "config/problem_configs/"

# # Variables
# obj = Variable("obj", type_tags=["locatable"])
# block, block_1, block_2 = variables("block block1 block2", types=["block"])
# loc, loc1, loc2, x = variables("loc loc1 loc2 x", types=["location"])
# robot = Variable("robot", type_tags=["robot"])

# # Predicates
# at = Predicate("at", obj, loc)
# on = Predicate("on", obj, loc)
# at_top = Predicate("at-top", block)
# gripper_empty = Predicate("gripper-empty")
# path_blocked = Predicate("path-blocked-from-to", loc1, loc2)

class PddlParser:
    def __init__(self, config_name: str,
                       domain_name: str,
                       problem_name: str,
                       problem_config_path: str = "config/problem_configs/") -> None:
        
        self.init_path = f"{problem_config_path}{config_name}/init.yaml"
        self.goal_path = f"{problem_config_path}{config_name}/goal.yaml"
        self.domain_name = domain_name
        self.problem_name = problem_name

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

            pos_name = "p" + str(len(self.positions)+1)
            pos = Constant(pos_name, type_tag="location")

            self.objects.append(obj)
            self.obj_constants[obj_name] = obj

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
                    self.init_predicates.append(predicates["gripper-empty"]())
                    continue

                case "at":
                    at_predicates = self.define_at_predicates(predicates["at"],
                                                              obj_constants,
                                                              position_constants)
                    self.init_predicates.append(at_predicates)
                    continue

                case "on":
                    continue

                case "at-top":
                    for obj_name, obj in obj_constants.items():
                        if obj_name[:5] == "block":
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

    def define_goal_conditions(self, goal_config: Dict) -> List:
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

        return goal_conds

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

def instantiate_predicates(objects: List[Constant]) -> List[Predicate]:
    return []