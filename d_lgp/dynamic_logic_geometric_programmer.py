from abc import abstractmethod
from typing import List, Tuple, Dict, Union, Callable, Type

from pypddl.core import States, State, Thing
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

    action_results = action(current_state, args)
    conflicts = action_results.failed_preconditions

    while conflicts:
        a_r, args, s = resolve_conflicts(states, conflicts)
        action_skeleton.insert(len(action_skeleton)-1, {'action': a_r, 'args': args})
        goals.insert(len(goals)-1, s)

        conflicts = action(s, args)

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

def resolve_conflicts(states: States, conflicts: List[Dict[str, Union[str, List[str]]]]) -> Tuple[Callable, Tuple[str, ...], List[State]]:
    return (callable, (), [])