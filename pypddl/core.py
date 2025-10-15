import copy

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Tuple, Union, Any, NewType, Type
from functools import wraps
from abc import abstractmethod

State = NewType("State", Dict[str, Dict[Tuple[str, ...], bool]])
Condition = NewType("Condition", Tuple[Callable, Dict[str, Type['Thing']], bool])

@dataclass
class Thing:
    name: str

@dataclass
class Pose(Thing):
    position: Tuple[float, float, float]
    oreintation: Tuple[float, float, float, float] = (0, 0, 0, 1)
    occupied_by: List[Any] = field(default_factory=lambda: [])

@dataclass
class Object(Thing):
    init_pose: Pose
    goal_pose: Pose = Pose("Nan", (-1, -1, -1))

    def __post_init__(self):
        self.pose = self.init_pose
        self.pose.occupied_by.append(self)

@dataclass
class Predicate:
    name: str
    evaluated_predicates: Dict[Tuple[str, ...], bool] = field(default_factory=lambda: {})

    @abstractmethod
    def eval(self, *args, **kwargs) -> bool:
        pass

    def update(self, *args):
        arg_names = tuple([arg.name for arg in args[:-1]])
        true = args[-1]

        if true is None:
            true = self.eval(*args[:-1])

        self.evaluated_predicates[arg_names] = true

    def __call__(self, *args) -> bool:
        arg_names = tuple([arg.name for arg in args])
        if arg_names not in self.evaluated_predicates.keys():
            self.evaluated_predicates[arg_names] = self.eval(*args)

        return self.evaluated_predicates[arg_names]

@dataclass
class States:
    objects: Dict[str, Object]
    poses: Dict[str, Pose]

    init_states: State
    states: List[State]
    goal_states: State

    predicates: Dict[str, Type[Predicate]] = field(default_factory=lambda: {})

    def get_obj_of_type(self, obj_name: str, type_: Any) -> Any:
        obj = self.objects[obj_name]

        assert isinstance(obj, type_), f"Object {obj.__class__.__name__} is not the specificed type: {type_.__name__}"
        return obj

    def initialize_states(self):
        self.states.append(self.init_states)
        self.states.append(self.goal_states)

    def update_states(self, state: State):
        self.states.insert(len(self.states)-1, state)

    @property
    def current_state(self):
        return self.states[-2]

    @property
    def goal_reached(self):
        goal_conds = []
        goal_state = self.goal_states
        final_state = self.states[-1]

        for name, cond in goal_state.items():
            corresponding_state = final_state[name]

            for goal_key in cond.keys():
                current_state_true = corresponding_state[goal_key]
                goal_conds.append(goal_key is current_state_true)

        return all(goal_conds)

@dataclass
class ActionResults:
    failed_preconds: List[Condition]
    new_state: State
    result: str

    @property
    def success(self):
        return self.failed_preconds == []

def action(preconds: List[Condition], effects: List[Condition]):
    def decorator(func):
        @wraps(func)

        def wrapper(state: State, **kwargs) -> ActionResults:
            failed_preconds = []
            new_state = copy.deepcopy(state)
            failed_preconds = find_failed_preconditions(state, kwargs, preconds)

            if failed_preconds == []:
                action_results = func(state, **kwargs)
                result = action_results.result

                for effect in effects:
                    effect_def, effect_name, effect_dict_keys, effect_args, true = unpack_conditions(effect, kwargs)
                    new_state[effect_name] = {effect_dict_keys: true}
                    effect_def.update(*effect_args, true)

            else:
                result = "Failed"

            return ActionResults(failed_preconds, new_state, result)
        return wrapper
    return decorator

def find_failed_preconditions(state: State, kwargs: Dict, preconditions: List[Condition]) -> List[Condition]:
    failed_preconditions = []
    for precond in preconditions:
        precond_def, precond_name, precond_dict_keys, precond_args, true = unpack_conditions(precond, kwargs)

        if precond_name not in state.keys():
            predicate = {precond_dict_keys: precond_def(*precond_args)}
            state[precond_name] = predicate
        else:
            predicate = state[precond_name]

            if precond_dict_keys not in predicate.keys():
                predicate[precond_dict_keys] = precond_def(*precond_args)

        if predicate[precond_dict_keys] != true:
            failed_preconditions.append({
                'name': precond_name,
                'args': precond_dict_keys,
                'cond': {'in state': predicate[precond_dict_keys],
                         'expected': true}
            })

    return failed_preconditions
    
def unpack_conditions(condition: Condition, kwargs: Dict) -> Tuple[Callable, str, Tuple[str, ...], List, bool]:
    cond_def, cond_types, true = condition
    cond_name = cond_def.name
    cond_type_names = cond_types.keys()

    cond_dict_keys = []
    cond_args = []

    for name in cond_type_names:
        cond_arg = kwargs[name]
        cond_dict_keys.append(cond_arg.name)
        cond_args.append(cond_arg)

    cond_dict_keys = tuple(cond_dict_keys)
    return cond_def, cond_name, cond_dict_keys, cond_args, true