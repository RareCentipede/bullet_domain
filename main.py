from yaml import safe_load
from pddl_parser.pddl_parser import PddlParser
from pddl.formatter import problem_to_string
from pddl import parse_domain

def main():
    pp = PddlParser("basic", "blocks", "blocks_basic")

    problem = pp.define_problem(problem_name="blocks_problem_1", save=True)

if __name__ == "__main__":
    main()