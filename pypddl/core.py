from dataclasses import dataclass, field
from typing import Optional, List, Dict, Callable, Tuple, Union, Any
from functools import wraps
from abc import abstractmethod

@dataclass
class Object:
    name: str
    init_pose: 'Pose'
    goal_pose: Optional['Pose'] = None

    def __post_init__(self):
        self.pose = self.init_pose
        self.pose.occupied_by = self

@dataclass
class Pose:
    name: str
    position: Tuple[float, float, float]
    oreintation: Tuple[float, float, float, float] = (0, 0, 0, 1)
    occupied_by: Optional[Any] = None

@dataclass
class Predicate:
    name: str
    evaluated_predicates: Dict[Tuple[str], bool] = field(default_factory=lambda: {})

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

def action(preconds: List[Tuple[str, Callable, List]], effect: Callable):
    def decorator(func):
        @wraps(func)

        def wrapper(*args, **kwargs):
            failed_preconds = []

            for name, precond, types in preconds:
                expected_args = [arg for arg in args if isinstance(arg, tuple(types))]
                if not precond(*expected_args):
                    failed_preconds.append({
                        'name': name,
                        'args': [(p.__class__.__name__, p.name) for p in expected_args],
                    })

            if failed_preconds:
                return failed_preconds

            effect(*args, **kwargs)
            func(*args, **kwargs)

            return failed_preconds
        return wrapper
    return decorator