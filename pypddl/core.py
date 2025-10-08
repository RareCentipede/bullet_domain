from dataclasses import dataclass
from typing import Optional, List, Dict, Callable, Tuple, Union, Any
from functools import wraps

@dataclass
class Object:
    name: str
    init_pose: 'Pose'
    goal_pose: Optional['Pose'] = None

    def __post_init__(self):
        self.pose = self.init_pose

@dataclass
class Pose:
    name: str
    position: Tuple[float, float, float]
    oreintation: Tuple[float, float, float, float] = (0, 0, 0, 1)
    occupied_by: Optional[Any] = None

def action(preconds: List[Tuple[str, Callable, List]], effect: Callable):
    def decorator(func):
        @wraps(func)

        def wrapper(*args, **kwargs):
            failed_preconds = []

            for name, precond, types in preconds:
                expected_types = [arg for arg in args if isinstance(arg, tuple(types))]
                if not precond(*expected_types):
                    failed_preconds.append({
                        'name': name,
                        'args': [p.__name__ for p in types],
                    })

            if failed_preconds:
                return failed_preconds

            func(*args, **kwargs)
            effect(*args, **kwargs)

            return failed_preconds
        return wrapper
    return decorator