import copy

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Callable, Tuple, Union, Any, NewType, Type
from functools import wraps
from abc import abstractmethod

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

State = NewType("State", Dict[str, Dict[Tuple[str, ...], bool]])

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
    failed_preconds: List[Tuple[Callable, Dict[str, Type[Thing]], bool]]
    new_state: State
    result: str

    @property
    def success(self):
        return self.failed_preconds == []

def action(preconds: List[Tuple[Callable, Dict[str, Type[Thing]], bool]], effects: List[Tuple[Callable, Dict[str, Type[Thing]], bool]]):
    def decorator(func):
        @wraps(func)

        def wrapper(state: State, **kwargs) -> ActionResults:
            failed_preconds = []
            new_state = copy.deepcopy(state)

            failed_preconds = find_failed_preconditions(state, kwargs, preconds)

            if failed_preconds == []:
                if 'init_pose' in kwargs.keys():
                    print()
                    print([o.name for o in kwargs['init_pose'].occupied_by])
                    print([o.name for o in kwargs['target_pose'].occupied_by])
                action_results = func(state, **kwargs)
                if 'init_pose' in kwargs.keys():
                    print()
                    print([o.name for o in kwargs['init_pose'].occupied_by])
                    print([o.name for o in kwargs['target_pose'].occupied_by])
                result = action_results.result

                # print("EFFECTS:")
                for effect in effects:
                    effect_pred, effect_args, true = effect
                    effect_name = effect_pred.name
                    arg_names = effect_args.keys()

                    inputs = []
                    pred_inputs = []
                    for name in arg_names:
                        kwarg = kwargs[name]
                        pred_inputs.append(kwarg)
                        inputs.append(kwarg.name)

                    inputs = tuple(inputs)
                    # print(effect_name, inputs, effect_pred(*pred_inputs), true)
                    new_state[effect_name] = {inputs: true}
                    effect_pred.update(*pred_inputs, true)
            else:
                result = "Failed"

            return ActionResults(failed_preconds, new_state, result)
        return wrapper
    return decorator

def find_failed_preconditions(state: State, kwargs: Dict,
                              preconditions: List[Tuple[Callable, Dict[str, Type[Thing]], bool]]) -> List[Tuple[Callable, Dict[str, Type[Thing]], bool]]:
    failed_preconditions = []
    for precond in preconditions:
        selected_inputs = {}
        pred, pred_args, true = precond
        pred_name = pred.name
        arg_names = tuple(pred_args.keys())

        for name in arg_names:
            kwarg = kwargs[name]
            selected_inputs[kwarg.name] = kwarg

        input_names = tuple(selected_inputs.keys())

        # print("PRECONDS:")
        if pred_name not in state.keys():
            corresponding_preds = {input_names: pred(*selected_inputs.values())}
            state[pred_name] = corresponding_preds
        else:
            corresponding_preds = state[pred_name]

        if input_names not in corresponding_preds.keys():
            corresponding_preds[input_names] = pred(*selected_inputs.values())

        # print(pred_name, input_names, corresponding_preds[input_names])

        if corresponding_preds[input_names] != true:
            failed_preconditions.append({
                'name': pred_name,
                'args': input_names,
                'cond': {'in state': corresponding_preds[input_names],
                         'expected': true}
            })

    return failed_preconditions
    