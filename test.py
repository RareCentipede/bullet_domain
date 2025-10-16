from enum import Enum # TODO Nice to use later for SAS+
from dataclasses import dataclass
from pypddl.block_domain import at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Block, Robot, move, grasp, place
from pddl_parser.problem_parser import parse_config_to_states

from d_lgp.dynamic_logic_geometric_programmer import dynamic_tree_search, successor_dagger, resolve_conflicts

def test():
    states = parse_config_to_states('basic')
    states.initialize_states()
    robot = states.get_obj_of_type('robot', Robot)
    block_2 = states.get_obj_of_type('block_2', Block)

    results = place(states.init_states, robot=robot, object=block_2, target_pose=block_2.goal_pose)
    print(results.new_state['at'])

    resolutions = resolve_conflicts(states, results.failed_preconds)

    # results = place(states.init_states, robot=robot, object=block_2, target_pose=block_2.goal_pose)
    # print(results.failed_preconds.keys())

    for res in resolutions:
        a, args, s = res
        # states.update_states(s)
        print("Resolving with action:", a.__name__, "and args:", [a.name for a in list(args.values())])
        # res = a(states.current_state, **args)
        # print(res.new_state['at'])
        # states.update_states(res.new_state)

    # results = place(states.current_state, robot=robot, object=block_2, target_pose=block_2.goal_pose)
    # print(results.failed_preconds.keys())
    # a, args = successor_dagger(states.current_state, states.goal_states)
    # params = states.objects[args[1]]
    # pose = states.poses[args[2]]
    # print(a(states.current_state, robot=robot, object=params, target_pose=pose).failed_preconds['holding'][0])

    # results = move(states.init_states, robot=robot, init_pose=robot.pose, target_pose=block_2.pose)
    # states.update_states(results.new_state)

    # results = grasp(states.current_state, robot=robot, target_object=block_2, object_pose=block_2.pose)
    # states.update_states(results.new_state)

    # results = move(states.current_state, robot=robot, init_pose=robot.pose, target_pose=block_2.goal_pose)
    # states.update_states(results.new_state)

    # results = place(states.current_state, robot=robot, object=block_2, target_pose=block_2.goal_pose)
    # states.update_states(results.new_state)

if __name__ == "__main__":
    test()