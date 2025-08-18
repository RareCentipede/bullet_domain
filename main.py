from yaml import safe_load
from pddl_parser.pddl_parser import parse_to_pddl, PddlParser
from pddl.formatter import problem_to_string
from pddl import parse_domain

def main():
    pp = PddlParser("basic", "blocks", "blocks_basic")

    objects, obj_constants, positions, position_constants = pp.define_init_objects(pp.init_config)
    init_predicates = pp.define_init_predicates(obj_constants, position_constants, pp.predicates)
    goal_conds = pp.define_goal_conditions(pp.goal_config)
    print(goal_conds)

    # # Load the YAML file
    # problem = parse_to_pddl("basic", "block_world", "test")

    # problem_str = problem_to_string(problem)

    # with open('pddl_worlds/blocks/blocks_problem.pddl', 'w') as f:
    #     f.write(problem_str)

    # domain_file = 'pddl_worlds/blocks/blocks_domain.pddl'

    # domain = parse_domain(domain_file)
    # print(domain.predicates)

    # print(problem)

    # print(list(problem.init)[0])

if __name__ == "__main__":
    main()