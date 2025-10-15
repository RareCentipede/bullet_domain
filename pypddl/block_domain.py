from dataclasses import dataclass
from typing import Optional, Type, Dict, Any
from pypddl.core import action, action2, Object, Pose, Predicate, State, States, ActionResults

# Domain specific objects
@dataclass
class Block(Object):
    on_top_of: Optional['Object'] = None
    below: Optional['Object'] = None

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
class NotAt(Predicate):
    name: str = 'not_at'

    def eval(self, obj: Object, pose: Pose) -> bool:
        return obj.pose != pose

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
        return pose.occupied_by is None

@dataclass
class PoseSupported(Predicate):
    name: str = 'pose_supported'

    def eval(self, pose: Pose) -> bool:
        return True


# Aliases for easier use in decorators
at = At()
not_at = NotAt()
gripper_empty = GripperEmpty()
at_top = AtTop()
holding = Holding()
clear = Clear()
pose_supported = PoseSupported()

# Domain specific states
# @dataclass
# class BlockStates(States):
#     predicates: Dict[str, Any] = {'at': at,
#                                   'gripper_empty': gripper_empty,
#                                   'at_top': at_top,
#                                   'holding': holding,
#                                   'clear': clear,
#                                   'pose_supported': pose_supported}

# Action definitions
@action(
    preconds=[('robot_not_at_target', not_at, [Robot, Pose])],
    effect=lambda robot, target_pose: (
        old_pose := robot.pose,
        at.update(robot, old_pose, False),
        not_at.update(robot, old_pose, True),

        setattr(robot.pose, 'occupied_by', None),
        setattr(robot, 'pose', target_pose),
    )
)
def move(robot: Robot, target_pose: Pose):
    print(f"Moving robot {robot.name} to pose {target_pose.name}: {target_pose.position}")

@action(
    preconds=[('robot_gripper_empty', gripper_empty, [Robot]),
              ('robot_at_picking_pose', at, [Robot, Pose]),
              ('object_at_picking_pose', at, [Block, Pose]),
              ('object_at_top', at_top, [Block])],
    effect=lambda robot, obj, pose: (
        gripper_empty.update(robot, False),
        holding.update(robot, obj, True),
        clear.update(pose, True),
        at.update(obj, obj.pose, False),
        not_at.update(obj, obj.pose, True),

        setattr(robot, 'gripper_empty', False),
        setattr(robot, 'holding', obj),
        setattr(obj.on_top_of, 'underneath', None) if obj.on_top_of else None,
        setattr(obj, 'on_top_of', None),
        setattr(pose, 'occupied_by', None),
    )
)
def grasp(robot: Robot, obj: Object, pose: Pose):
    print(f"Robot {robot.name} grasps object {obj.name} at pose {pose.name}: {pose.position}")

@action(
    preconds=[('robot_holding_obj', holding, [Robot, Block]),
              ('robot_at_placing_pose', at, [Robot, Pose]),
              ('placing_pose_clear', clear, [Pose]),
              ('position_supported', pose_supported, [Pose])],
    effect=lambda robot, obj, target_pose: (
        not_at.update(obj, obj.pose, True),
        at.update(obj, target_pose, True),
        gripper_empty.update(robot, True),
        holding.update(robot, obj, False),
        clear.update(target_pose, False),
        at_top.update(obj, True),

        setattr(obj, 'pose', target_pose),
        setattr(robot, 'gripper_empty', True),
        setattr(robot, 'holding', None),
        setattr(target_pose, 'occupied_by', obj),
        support_block := None,
        setattr(obj, 'on_top_of', support_block),
        setattr(support_block, 'underneath', obj) if support_block is not None else None

    )
)
def place(robot: Robot, obj: Block, target_pose: Pose):
    print(f"Robot {robot.name} places object {obj.name} on support {obj.on_top_of.name if obj.on_top_of is not None else 'ground'} at pose {target_pose.name}: {target_pose.position}")

@action2(
    preconds=[
        (at, {'robot': Robot, 'init_pose': Pose}, True),
        (at, {'robot': Robot, 'target_pose': Pose}, False)],
    effects=[
        (at, {'robot': Robot, 'init_pose': Pose}, False),
        (at, {'robot': Robot, 'target_pose': Pose}, True)]
)
def move2(state: State, robot: Robot, init_pose: Pose, target_pose: Pose) -> ActionResults:
    init_pose.occupied_by = None
    target_pose.occupied_by = robot

    robot.pose = target_pose
    print(f"Moving robot {robot.name} from {init_pose.name}: {init_pose.position} to {target_pose.name}: {target_pose.position}")

    res_str = f"Movved {robot.name} from {init_pose.name}: {init_pose.position} to {target_pose.name}: {target_pose.position}"

    return ActionResults([], None, res_str)