from pypddl.block_domain import at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Object, Pose, Block, Robot, move, grasp, place, move2
from pypddl.core import States, State, ActionResults
from pddl_parser.problem_parser import parse_config_to_states

def test():
    states = parse_config_to_states('basic')
    states.initialize_states()
    robot = states.get_obj_of_type('robot', Robot)
    block_2 = states.get_obj_of_type('block_2', Block)
    pose_2 = states.poses['p2']

    one_state = states.init_states

    action_results = move2(one_state, robot=robot, init_pose=robot.pose, target_pose=pose_2)
    print(action_results)

    move(robot, block_2.pose)
    grasp(robot, block_2, block_2.pose)
    move(robot, block_2.goal_pose)
    place(robot, block_2, block_2.goal_pose)

if __name__ == "__main__":
    test()