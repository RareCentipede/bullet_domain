from pddl_parser.pddl_parser import PddlProblemParser, parse_plan
from dispatcher.dispatcher import CommandDispatcher
from pathlib import Path
from os import listdir

import subprocess

def solve_pddl_problem(domain_name: str, problem_name: str, solver: str = "downward", plan_dir: str = "plans/"):
    domain = f"pddl_worlds/blocks/{domain_name}_domain.pddl"
    problem = f"pddl_worlds/blocks/{problem_name}.pddl"

    home = Path.home()
    cmd = f"{home}/downward/fast-downward.py --plan-file {plan_dir}{problem_name}/plan_lama --alias seq-sat-lama-2011 {domain} {problem}"

    match solver:
        case "downward":
            subprocess.run(cmd.split())

        case _:
            print(f"Undefined solver {solver}")
            raise NotImplementedError()

def main():
    problem_name = "blocks_problem_1"

    pp = PddlProblemParser("basic", "blocks")
    pp.define_problem(problem_name=problem_name, save=True)

    solve_pddl_problem("blocks", problem_name)

    plans_dir = f"plans/{problem_name}/"
    plan_file = listdir(plans_dir)[-1]
    plan = parse_plan(plans_dir + plan_file)
    print(plan)

    cd = CommandDispatcher(pp.init_predicates, pp.positions)
    cd.initialize_objects()
    cd.run_simulation(plan)

if __name__ == "__main__":
    main()