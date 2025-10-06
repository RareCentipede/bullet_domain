from dataclasses import dataclass
from typing import Optional, List, Dict, Callable, Tuple
from functools import wraps

@dataclass
class Types:
    robot: str = 'robot'
    location: str = 'location'
    object: str = 'object'

@dataclass
class Object:
    name: str
    pos: List[float]
    _type: str = Types.object

    def __post_init__(self):
        assert len(self.pos) == 3, "Position must be 3D"

@dataclass
class Location(Object):
    _type: str = Types.location

@dataclass
class Robot(Object):
    gripper_empty: bool = True
    holding: Optional[Object] = None
    _type: str = Types.robot

@dataclass
class at:
    obj: Object
    loc: Location

    def __call__(self) -> bool:
        return self.obj.pos == self.loc.pos

def define_at_predicates(obj: Object, loc: Location) -> bool:
    return obj.pos == loc.pos

def define_not_at_predicates(obj: Object, loc: Location) -> bool:
    return obj.pos != loc.pos

# @dataclass
# class Action:
#     name: str
#     parameters: List[str]
#     preconditions: List[Predicate]
#     effects: List[Callable[..., None]]

#     def is_applicable(self, *args, **kwargs) -> bool:
#         return all(precond(*args, **kwargs) for precond in self.preconditions)

#     def apply(self, *args, **kwargs):
#         if not self.is_applicable(*args, **kwargs):
#             raise Exception("Preconditions not satisfied")
#         for effect in self.effects:
#             effect(*args, **kwargs)

def is_move_action_valid(robot: Robot, start: Location, dest: Location) -> bool:
    if not at(robot, start):
        print("Robot not at the start location")
        return False
    elif at(robot, dest):
        print("Robot already at the destination")
        return False

    return True

def move_action(robot: Robot, start: Location, dest: Location):
    pass

# def action(preconditions: List[Predicate] = []):
#     preconditions = preconditions or []
#     def decorator(action_func: Callable):
#         @wraps(action_func)
#         def wrapper(*args, **kwargs):
#             failed_preconds = []
#             for precond in preconditions:
#                 if not precond(*args, **kwargs):
#                     failed_preconds.append(precond)
#             if failed_preconds:
#                 return failed_preconds

#             return action_func(*args, **kwargs)
#         return wrapper
#     return decorator

larry = Robot(name='larry', pos=[0, 0, 0])
p_larry = Location(name='p_larry', pos=[1, 0, 0])
print(larry)

# @action(preconditions=[at, not_at])
# def move(robot: Robot, start: Location, destination: Location):
#     robot.pos = destination.pos

# results = move(larry, p_larry)
# if results is not None:
#     print("Failed preconditions:")
#     for p in results:
#         print(f"- {p.name}")