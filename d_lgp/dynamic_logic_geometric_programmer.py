from abc import abstractmethod
from typing import List, Tuple, Dict, Union, Callable

from pypddl.core import States, State
from pypddl.block_domain import at, not_at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Object, Pose, Block, Robot, move, grasp, place

def conflict_driven_task_graph(states: States, action_skeleton: List, goals: List) -> None:
    current_state = states.states[-2]
    goal_state = states.goal_states

    action, args = successor_dagger(current_state, goal_state)
    action_skeleton.append({'action': action, 'args': args})

    conflicts = action(args)

    while conflicts:
        a_r, args, s = resolve_conflicts(states, conflicts)
        action_skeleton.insert(len(action_skeleton)-2, a_r)
        goals.insert(len(goals)-2, s)

        conflicts = action(args)

def successor_dagger(current_state: State, goal_state: State) -> Tuple[Callable, Tuple[str, ...]]:
    return (callable, ())

def successor(current_state: State, action: str, action_args: Tuple[str, ...]) -> State:
    return State({})

def resolve_conflicts(states: States, conflicts: List[Dict[str, Union[str, List[str]]]]) -> Tuple[Callable, Tuple[str, ...], List[State]]:
    return (callable, (), [])