from abc import abstractmethod
from typing import List, Tuple, Dict, Union, Callable, Type

from pypddl.core import States, State, Thing, Condition, ActionResults
from pypddl.block_domain import at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Object, Pose, Block, Robot, move, grasp, place

def dynamic_tree_search(states: States) -> Tuple[List[Dict[str, Union[List[Callable], List[str]]]], List[State]]:
    action_skeleton, goals = [], []

    conflict_driven_task_graph(states, action_skeleton, goals)

    while not states.goal_reached:
        last_feasible_action, last_feasible_action_args = action_skeleton[-1].items()

        action_results = last_feasible_action(states.current_state, *last_feasible_action_args)
        next_state = action_results.new_state
        states.update_states(next_state)

        conflict_driven_task_graph(states, action_skeleton, goals)

    return action_skeleton, goals

def conflict_driven_task_graph(states: States, action_skeleton: List, goals: List) -> None:
    current_state = states.current_state
    goal_state = states.goal_states

    action, args = successor_dagger(current_state, goal_state)
    action_skeleton.append({'action': action, 'args': args})

    print(args) # args from successor dagger not in proper format

    action_results = action(current_state, args)
    conflicts = [action_results.failed_preconds]

    conflict_index = 0

    while conflicts != []:
        conflict_name, conflict = list(conflicts[0].items())[0]
        a_r, args = resolve_conflicts(states, conflict_name, conflict)

        current_state = states.current_state
        action_results = action(current_state, args)
        new_conflicts = action_results.failed_preconds

        if new_conflicts:
            conflicts.insert(0, new_conflicts)
        else:
            action_skeleton.insert(len(action_skeleton)-1, {'action': a_r, 'args': args})
            goals.insert(len(goals)-1, current_state)
            states.update_states(action_results.new_state)

        # conflicts.insert(0, action(s, args).failed_preconds)

    goals.append(goal_state)

def successor_dagger(current_state: State, goal_state: State) -> Tuple[Callable, Tuple[str, ...]]:
    goal = ()

    # Select a goal state
    for args, true in goal_state['at'].items():
        if not true:
            args = list(args)
            args.insert(0, 'at')
            goal = tuple(args)
            break

    return place, goal

def resolve_conflicts(states: States, conflict_name: str, conflict: Condition) -> Tuple[Callable, Dict[str, Type[Thing]]]:
    robot = states.get_obj_of_type('robot', Robot)
    resolutions = []

    match conflict_name:
        case 'holding':
            print("Resolving holding conflict...")
            missing_obj = list(conflict[1].values())[1]

            if isinstance(missing_obj, Block):
                # results = grasp(states.current_state, robot=robot, target_object=missing_obj, object_pose=missing_obj.pose)
                resolution_callable = grasp
                resolution_args = {'robot': robot, 'target_object': missing_obj, 'object_pose': missing_obj.pose}

        case 'at':
            print("Resolving at conflict...")
            target_pose = list(conflict[1].values())[1]

            if isinstance(target_pose, Pose):
                # results = move(states.current_state, robot=robot, init_pose=robot.pose, target_pose=target_pose)
                resolution_callable = move
                resolution_args = {'robot': robot, 'init_pose': robot.pose, 'target_pose': target_pose}

        case _:
            raise NotImplementedError(f"Conflict {conflict_name} not implemented yet or doesn't exist.")

    print(resolution_args)

    resolutions = (resolution_callable, resolution_args)
    return resolutions