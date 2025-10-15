from pypddl.block_domain import at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Block, Robot, move, grasp, place
from pddl_parser.problem_parser import parse_config_to_states

def test():
    states = parse_config_to_states('basic')
    states.initialize_states()
    robot = states.get_obj_of_type('robot', Robot)
    block_2 = states.get_obj_of_type('block_2', Block)

    results = move(states.init_states, robot=robot, init_pose=robot.pose, target_pose=block_2.pose)
    states.update_states(results.new_state)

    results = grasp(states.current_state, robot=robot, target_object=block_2, object_pose=block_2.pose)
    states.update_states(results.new_state)

    results = move(states.current_state, robot=robot, init_pose=robot.pose, target_pose=block_2.goal_pose)
    states.update_states(results.new_state)

    results = place(states.current_state, robot=robot, object=block_2, target_pose=block_2.goal_pose)
    states.update_states(results.new_state)

if __name__ == "__main__":
    test()