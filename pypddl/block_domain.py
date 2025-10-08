from dataclasses import dataclass
from typing import Optional, List, Dict, Callable, Tuple, Union, Any
from core import action, Object, Pose
from abc import abstractmethod

@dataclass
class Block(Object):
    on_top_of: Optional['Object'] = None
    underneath: Optional['Object'] = None

@dataclass
class Robot(Object):
    gripper_empty: bool = True
    holding: Optional[Object] = None

# Predicate functions
class States:
    def __init__(self, supporting_obj: Block):
        self.supporting_object = supporting_obj

    @staticmethod
    def at(obj: Object, pose: Pose) -> bool:
        return obj.pose == pose

    @staticmethod
    def not_at(obj: Object, pose: Pose) -> bool:
        return obj.pose != pose

    @staticmethod
    def gripper_empty(robot: Robot) -> bool:
        return robot.gripper_empty

    @staticmethod
    def at_top(blk: Block) -> bool:
        return blk.underneath is None

    @staticmethod
    def holding(robot: Robot, obj: Object) -> bool:
        return robot.holding == obj

    @staticmethod
    def clear(pose: Pose) -> bool:
        return pose.occupied_by is None

    @staticmethod
    def pose_supported(pose: Pose) -> bool:
        return True # Simplified for now

    def find_supportting_object(self, pose: Pose) -> Block:
        return self.supporting_object

# Aliases for easier use in decorators
at = States.at
not_at = States.not_at
gripper_empty = States.gripper_empty
at_top = States.at_top
holding = States.holding
clear = States.clear
pose_supported = States.pose_supported

support_block = Block(name='support', init_pose=Pose(name='support_pose', position=(0,0,0)))
states = States(support_block)
find_supportting_object = states.find_supportting_object

# Action definitions
@action(
    preconds=[('robot_not_at_target', not_at, [Robot, Pose])],
    effect=lambda robot, target_pose: (
        setattr(robot.pose, 'occupied_by', None),
        setattr(robot, 'pose', target_pose)
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
        setattr(robot, 'gripper_empty', True),
        setattr(robot, 'holding', None),
        setattr(target_pose, 'occupied_by', obj)
    )
)
def place(robot: Robot, obj: Block, target_pose: Pose):
    # Extra effects
    support_obj = find_supportting_object(target_pose)
    obj.on_top_of = support_obj

    setattr(obj, 'on_top_of', support_obj)
    setattr(support_obj, 'underneath', obj)

    print(f"Robot {robot.name} places object {obj.name} on support {obj.on_top_of.name} at pose {target_pose.name}: {target_pose.position}")

p1 = Pose(name='p1', position=(0, 0, 0))
p2 = Pose(name='p2', position=(1, 0, 0))
p3 = Pose(name='p3', position=(0, 1, 0))
larry = Robot(name='Larry', init_pose=p1)

b1 = Block(name='b1', init_pose=p2, goal_pose=p3)

failed_preconds = move(larry, p2)
if failed_preconds:
    for p in failed_preconds: # type: ignore
        print(f"Failed precondition: {p['name']} with args {p['args']}")
else:
    grasp(larry, b1, p2)
    move(larry, p3)
    place(larry, b1, p3)