from abc import abstractmethod
from pddl.logic import Predicate, constants, variables, Variable, Constant
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.requirements import Requirements
from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem

from yaml import safe_load
from typing import Dict, List, Union

problem_config_path = "config/problem_configs/"

# Variables
obj = Variable("obj", type_tags=["locatable"])
block, block_1, block_2 = variables("block block1 block2", types=["block"])
loc, loc1, loc2, x = variables("loc loc1 loc2 x", types=["location"])
robot = Variable("robot", type_tags=["robot"])

# Predicates
at = Predicate("at", obj, loc)
on = Predicate("on", obj, loc)
at_top = Predicate("at-top", block)
gripper_empty = Predicate("gripper-empty")
path_blocked = Predicate("path-blocked-from-to", loc1, loc2)

class PddlParser:
    def __init__(self, config_name: str,
                       domain_name: str,
                       problem_name: str,
                       problem_config_path: str = "config/problem_configs") -> None:
        
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
        self.blk_constants = {}
        self.position_constants = {}

def parse_to_pddl(config_name: str, domain_name: str, problem_name: str) -> Problem:
    init_path = f"{problem_config_path}{config_name}/init.yaml"
    goal_path = f"{problem_config_path}{config_name}/goal.yaml"

    with open(init_path, 'r') as f:
        init_config = safe_load(f)

    with open(goal_path, 'r') as f:
        goal_config = safe_load(f)

    obj_dict = init_config['objects']
    blk_names = obj_dict.keys()
    blk_constants = {}
    objects = []
    init = [gripper_empty()]
    goal = []
    positions = {}

    for blk_name in blk_names:
        # Define the objects
        blk = obj_dict[blk_name]

        type = 'static' if blk['static'] else 'dynamic'

        blk_constant = Constant(blk_name, type_tag=type)
        objects.append(blk_constant)
        blk_constants[blk_name] = blk_constant

        pos_name = "p" + blk_name[-1]
        positions[pos_name] = blk['position']
        pos_constant = Constant(pos_name, type_tag="location")
        objects.append(pos_constant)

        # Define initial states
        at_predicate = at(blk_constant, pos_constant)
        at_top_predicate = at_top(blk_constant)
        init.append(at_predicate)
        init.append(at_top_predicate)

    larry = Constant("larry", type_tag="robot")
    robot_pos_constant = Constant("pr", type_tag="location")
    init.append(at(larry, robot_pos_constant))
    objects.append(larry)
    objects.append(robot_pos_constant)

    # Define goal states
    objs_goal = goal_config['objects']

    for blk_name, content in objs_goal.items():
        blk_constant = blk_constants[blk_name]
        pos = content['position']

        if pos in positions.values():
            pos_name = list(positions.keys())[list(positions.values()).index(pos)]
        else:
            pos_name = "p" + str(len(positions)+1)
            positions[pos_name] = pos

        pos_constant = Constant(pos_name, type_tag="location")
        objects.append(pos_constant)

        at_predicate = at(blk_constant, pos_constant)
        goal.append(at_predicate)

    goal_conds = goal[0]

    for g in goal[1:]:
        goal_conds = goal_conds & g

    problem = Problem(name=problem_name,
                      domain_name=domain_name,
                      objects=objects,
                      init=init,
                      goal=goal_conds
                     )

    return problem

def define_objects(objects: Dict[str, str]) -> List[Constant]:
    """
        Parameters:
            objects: Dictionary(object_name)
        Defines
            - Statics and dynamic blocks
            - Positions
    """
    return []

def instantiate_predicates(objects: List[Constant]) -> List[Predicate]:
    return []