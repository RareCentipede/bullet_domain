from dataclasses import dataclass
from typing import Optional
from pypddl.core import action, Object, Pose, Predicate, State, ActionResults, Condition

# Domain specific objects
@dataclass
class Block(Object):
    on_top_of: Optional[Object] = None
    below: Optional[Object] = None

@dataclass
class Robot(Object):
    gripper_empty: bool = True
    holding: Optional[Object] = None

# Predicates
@dataclass
class At(Predicate):
    name: str = 'at'

    def eval(self, obj: Object, pose: Pose) -> bool:
        return obj.pose == pose

@dataclass
class GripperEmpty(Predicate):
    name: str = 'gripper_empty'

    def eval(self, robot: Robot) -> bool:
        return robot.gripper_empty

@dataclass
class AtTop(Predicate):
    name: str = 'at_top'

    def eval(self, block: Block) -> bool:
        return block.below is None

@dataclass
class Holding(Predicate):
    name: str = 'holding'

    def eval(self, robot: Robot, obj: Object) -> bool:
        return robot.holding == obj

@dataclass
class Clear(Predicate):
    name: str = 'clear'

    def eval(self, pose: Pose) -> bool:
        return pose.occupied_by == [] or (len(pose.occupied_by) == 1 and type(pose.occupied_by) == Robot)

@dataclass
class PoseSupported(Predicate):
    name: str = 'pose_supported'

    def eval(self, pose: Pose) -> bool:
        return True

# Aliases for easier use in decorators
at = At()
gripper_empty = GripperEmpty()
at_top = AtTop()
holding = Holding()
clear = Clear()
pose_supported = PoseSupported()

# Action definitions
@action(
    preconds=[
        Condition((at, {'robot': Robot, 'init_pose': Pose}, True)),
        Condition((at, {'robot': Robot, 'target_pose': Pose}, False))
    ],
    effects=[
        Condition((at, {'robot': Robot, 'init_pose': Pose}, False)),
        Condition((at, {'robot': Robot, 'target_pose': Pose}, True))
    ]
)
def move(state: State, robot: Robot, init_pose: Pose, target_pose: Pose) -> ActionResults:
    init_pose.occupied_by.remove(robot)
    target_pose.occupied_by.append(robot)
    robot.pose = target_pose

    res_str = f"Moved {robot.name} from {init_pose.name}: {init_pose.position} to {target_pose.name}: {target_pose.position}"
    print(res_str)

    return ActionResults([], state, res_str)

@action(
    preconds=[
        Condition((gripper_empty, {'robot': Robot}, True)),
        Condition((at, {'robot': Robot, 'object_pose': Pose}, True)),
        Condition((at, {'target_object': Block, 'object_pose': Pose}, True)),
        Condition((at_top, {'target_object': Block}, True))
    ],
    effects=[
        Condition((gripper_empty, {'robot': Robot}, False)),
        Condition((holding, {'robot': Robot, 'target_object': Block}, True)),
        Condition((clear, {'object_pose': Pose}, True)),
        Condition((at, {'target_object': Block, 'object_pose': Pose}, False))
    ]
)
def grasp(state: State, robot: Robot, target_object: Block, object_pose: Pose) -> ActionResults:
    robot.gripper_empty = False
    robot.holding = target_object
    object_pose.occupied_by.remove(target_object)
    target_object.pose = Pose('nan', (-1, -1, -1))

    below_obj = target_object.on_top_of
    if isinstance(below_obj, Block):
        below_obj.below = None

    target_object.on_top_of = None

    res_str = f"Robot {robot.name} grasps object {target_object.name} at pose {object_pose.name}: {object_pose.position}"
    print(res_str)

    return ActionResults([], state, res_str)

@action(
    preconds=[
        Condition((holding, {'robot': Robot, 'object': Block}, True)),
        Condition((at, {'robot': Robot, 'target_pose': Pose}, True)),
        Condition((clear, {'target_pose': Pose}, True)),
        Condition((pose_supported, {'target_pose': Pose}, True))
    ],
    effects=[
        Condition((at, {'object': Block, 'target_pose': Pose}, True)),
        Condition((gripper_empty, {'robot': Robot}, True)),
        Condition((holding, {'robot': Robot, 'object': Block}, False)),
        Condition((clear, {'target_pose': Pose}, False)),
        Condition((at_top, {'object': Block}, True))
    ]
)
def place(state: State, robot: Robot, object: Block, target_pose: Pose) -> ActionResults:
    object.pose = target_pose
    robot.gripper_empty = True
    robot.holding = None
    target_pose.occupied_by.append(object)

    support_block = None
    object.on_top_of = support_block

    if isinstance(support_block, Block):
        support_block.below = object

    res_str = f"Robot {robot.name} places object {object.name} on support {object.on_top_of.name if object.on_top_of is not None else 'ground'} at pose {target_pose.name}: {target_pose.position}"
    print(res_str)

    return ActionResults([], state, res_str)