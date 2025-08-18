from yaml import safe_load
from pddl_parser.pddl_parser import parse_to_pddl
from pddl.formatter import problem_to_string
from pddl import parse_domain

def main():
    # Load the YAML file
    problem = parse_to_pddl("basic", "block_world", "test")

    problem_str = problem_to_string(problem)

    with open('pddl_worlds/blocks/block_problem.pddl', 'w') as f:
        f.write(problem_str)

    domain_file = 'pddl_worlds/blocks/block_domain.pddl'

    print(domain_file)
    domain = parse_domain(domain_file)
    pred_list = list(domain.predicates)
    pred = pred_list[0]
    print(pred.name, pred.terms[0].name, list(pred.terms[0].type_tags)[0])

    # print(list(problem.init)[0])

if __name__ == "__main__":
    main()