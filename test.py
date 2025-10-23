from enum import Enum, auto # TODO Nice to use later for SAS+
from dataclasses import dataclass
from pypddl.block_domain import at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Block, Robot, move, grasp, place
from pddl_parser.problem_parser import parse_config_to_states

from d_lgp.dynamic_logic_geometric_programmer import dynamic_tree_search, successor_dagger, resolve_conflicts, conflict_driven_task_graph

def test():
    states = parse_config_to_states('basic')
    states.initialize_states()
    robot = states.get_obj_of_type('robot', Robot)
    block_2 = states.get_obj_of_type('block_2', Block)

    p1 = states.poses['p1']
    p2 = states.poses['p2']
    p3 = states.poses['p3']

    @dataclass
    class PosEnum:
        position: Enum

    poses = states.poses
    # add any new poses first so the Enum includes them
    poses['new_pose'] = p1
    Pos = Enum('Pos', poses)
    # pos_enum = PosEnum(position=Pos['p1'])

    @dataclass
    class RobotPos:
        position: Pos

    robot_pos = RobotPos(position=Pos['p1'])
    robot_pos.position = Pos['p2']
    print(robot_pos.position.value)

    robot_pos.position = Pos['new_pose']
    print(robot_pos.position.value)

    # action_skeleton, goals = dynamic_tree_search(states)
    # # conflict_driven_task_graph(states, action_skeleton, goals)
    # print("Action Skeleton:")

    # for action in action_skeleton:
    #     a, args = action.items()
    #     print(f"Action: {a[1].__name__}")

    #     print("Args:")
    #     for arg in args[1].values():
    #         print(arg.name if type(arg) != dict else "state")
            # print(arg.name)
    # failed_preconds = results.failed_preconds
    # print(failed_preconds.keys())
    # print(resolutions)

    # results = place(states.init_states, robot=robot, object=block_2, target_pose=block_2.goal_pose)
    # print(results.failed_preconds.keys())
                               
    # for res in resolutions:
        # a, args, s = res
        # states.update_states(s)
        # print("Resolving with action:", a.__name__, "and args:", [a.name for a in list(args.values())])
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