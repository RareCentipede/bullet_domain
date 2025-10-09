import numpy as np

from yaml import safe_load
from typing import Dict, List, Union, Tuple, Optional, TypeVar, Generic

from scipy.spatial import KDTree
from pypddl.block_domain import at, not_at, gripper_empty, at_top, holding, clear, pose_supported, At
from pypddl.block_domain import Object, Pose, Block, Robot, States

def parse_config_to_states(config_name: str, problem_config_path: str = "config/problem_configs/") -> States:
    states = States({}, {}, {}, {})

    init_config, goal_config = load_configs_to_dicts(config_name, problem_config_path)
    define_init_objects_and_poses(states, init_config)
    define_goal_objects_and_poses(states, goal_config)

    build_physical_relations(states)
    define_init_predicates(states)

    return states

def load_configs_to_dicts(config_name: str, problem_config_path: str) -> Tuple[Dict, Dict]:
    init_path = f"{problem_config_path}{config_name}/init.yaml"
    goal_path = f"{problem_config_path}{config_name}/goal.yaml"

    with open(init_path, 'r') as f:
        init_config = safe_load(f)
        f.close()

    with open(goal_path, 'r') as f:
        goal_config = safe_load(f)
        f.close()

    return init_config, goal_config

def define_init_objects_and_poses(states: States, init_config: Dict):
    idx = 1
    for obj_name, info in init_config.items():
        obj_type = obj_name.split('_')[0]

        pose_name = "p" + str(idx)
        pose = Pose(pose_name, info["position"])

        if obj_type == "block":
            obj = Block(obj_name, pose)
            pose.occupied_by = obj
        else:
            obj = Robot(obj_name, pose)

        states.objects[obj_name] = obj
        states.poses[pose_name] = pose

        at(obj, pose)
        idx += 1

    states.init_states['at'] = at.evaluated_predicates

def define_goal_objects_and_poses(states: States, goal_config: Dict):
    goal_at = At()
    for obj_name, info in goal_config.items():
        pos = info['position']
        pose_name = find_pose_from_value(states.poses, pos)

        if pose_name is None:
            pose_name = "p" + str(len(states.poses)+1)
            pose = Pose(pose_name, pos)
            states.poses[pose_name] = pose
        else:
            pose = states.poses[pose_name]

        states.objects[obj_name].goal_pose = pose
        goal_at(states.objects[obj_name], pose)

    states.goal_states['at'] = goal_at.evaluated_predicates

def find_pose_from_value(poses: Dict[str, Pose], pos: List[float]) -> Optional[str]:
    pose_names = poses.keys()
    pose_coords = [p.position for p in poses.values()]

    if pos not in pose_coords:
        return None

    pose_idx = pose_coords.index(pos)
    pos_name = list(pose_names)[pose_idx]

    return pos_name

def build_physical_relations(states: States):
    """
        Go through the objects and determine their relations with each other.
    """
    visited_obj_ids= []
    stacks = []

    objs = list(states.objects.values())
    obj_positions = [obj.pose.position[:2] for obj in objs]

    obj_tree = KDTree(obj_positions)
    for i, pos in enumerate(obj_positions):
        if i in visited_obj_ids:
            continue

        obj_idx_in_stack = obj_tree.query_ball_point(pos, 0.5)
        visited_obj_ids.extend(obj_idx_in_stack)

        objs_in_stack = np.array(objs)[obj_idx_in_stack]
        objs_in_stack = sorted(objs_in_stack, key=lambda obj: (obj.pose.position[-1]))

        stacks.append([obj.name for obj in objs_in_stack])

    for stack in stacks:
        for i in range(len(stack)-1):
            obj_name = stack[i]
            obj = states.get_obj_type(obj_name, Block)

            above_obj_name = stack[i+1]

            above_obj = states.get_obj_type(above_obj_name, Block)
            obj.below = above_obj
            above_obj.on_top_of = obj

def define_init_predicates(states: States):
    for obj, pose in zip(states.objects.values(), states.poses.values()):
        if type(obj) is Block:
            at_top(obj)

        clear(pose)

    for pose in list(states.poses.values())[len(states.objects):]:
        clear(pose)

    states.init_states['at_top'] = at_top.evaluated_predicates
    states.init_states['clear'] = clear.evaluated_predicates