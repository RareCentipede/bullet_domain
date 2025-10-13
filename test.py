from pypddl.block_domain import at, not_at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Object, Pose, Block, Robot, States, move, grasp, place
from pddl_parser.problem_parser import parse_config_to_states

predicate_dict = {'at': at,
                  'not_at': not_at,
                  'gripper_empty': gripper_empty,
                  'at_top': at_top,
                  'holding': holding,
                  'clear': clear,
                  'pose_supported': pose_supported}

def test():
    states = parse_config_to_states('basic')
    robot = states.get_obj_of_type('robot', Robot)
    block_2 = states.get_obj_of_type('block_2', Block)

    print(at.evaluated_predicates)

    for p in states.init_states.values():
        print(all(list((p.values()))))

    move(robot, block_2.pose)
    grasp(robot, block_2, block_2.pose)
    move(robot, block_2.goal_pose)
    place(robot, block_2, block_2.goal_pose)

if __name__ == "__main__":
    test()