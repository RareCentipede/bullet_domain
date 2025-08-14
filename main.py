from yaml import safe_load
from pddl_parser.pddl_parser import parse_to_pddl

def main():
    # Load the YAML file
    problem = parse_to_pddl("basic", "test", "test")

if __name__ == "__main__":
    main()