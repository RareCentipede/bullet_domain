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
    problem_name = "blocks_problem_3"

    pp = PddlProblemParser("many_stacked", "blocks")
    pp.define_problem(problem_name=problem_name, save=True)

    solve_pddl_problem("blocks", problem_name)

    plans_dir = f"./plans/{problem_name}/"

    try:
        plan_files = listdir(plans_dir)
    except:
        subprocess.run(["mkdir", plans_dir])
        plan_files = listdir(plans_dir)[-1]

    plan_file_nums = [int(f[-1]) for f in plan_files]
    plan_file = plan_files[plan_file_nums.index(max(plan_file_nums))]
    plan = parse_plan(plans_dir + plan_file)

    print(pp.positions)
    cd = CommandDispatcher(pp.init_predicates, pp.positions)
    cd.initialize_objects()
    cd.run_simulation(plan)
    # cd.run_simulation([("", [" ", " "])])

if __name__ == "__main__":
    main()