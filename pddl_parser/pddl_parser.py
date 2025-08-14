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

def parse_to_pddl(config_name: str, domain_name: str, problem_name: str) -> Problem:
    init_path = f"{problem_config_path}{config_name}/init.yaml"
    goal_path = f"{problem_config_path}{config_name}/goal.yaml"

    with open(init_path, 'r') as f:
        init_config = safe_load(f)

    with open(goal_path, 'r') as f:
        goal_config = safe_load(f)

    print(f"init config:\n{init_config}\n")
    print(f"goal config: \n{goal_config}")

    problem = Problem(name=problem_name,
                      domain_name=domain_name)

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