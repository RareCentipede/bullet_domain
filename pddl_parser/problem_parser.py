import copy
import numpy as np

from yaml import safe_load
from typing import Dict, List, Union, Tuple, Optional
from dataclasses import replace
from abc import abstractmethod

from scipy.spatial import KDTree
from pypddl.block_domain import at, not_at, gripper_empty, at_top, holding, clear, pose_supported
from pypddl.block_domain import Object, Pose, Block, Robot, States, move, grasp, place

problem_config_path = "config/problem_configs/"

class ProblemParser:
    def __init__(self, config_name: str,
                       problem_config_path: str = "config/problem_configs/") -> None:
        
        self.init_path = f"{problem_config_path}{config_name}/init.yaml"
        self.goal_path = f"{problem_config_path}{config_name}/goal.yaml"

        with open(self.init_path, 'r') as f:
            self.init_config = safe_load(f)
            f.close()

        with open(self.goal_path, 'r') as f:
            self.goal_config = safe_load(f)
            f.close()

def parse_config_to_states(config_name: str, problem_config_path: str = "config/problem_configs/") -> States:
    states = States({}, {}, {}, {})

    """
        - Open files and load content to dictionaries
        - Define objects and poses, add them to statets
        - Define init and goal predicates
    """
    init_config, goal_config = load_configs_to_dicts(config_name, problem_config_path)

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

def define_objects_poses_in_states(states: States, init_config: Dict, goal_config: Dict) -> States:
    idx = 0
    for obj_name, info in init_config.items():
        obj_type = obj_name.split('_')[0]

        pose_name = "p" + str(idx)
        pose = Pose(pose_name, info["position"])

        if obj_type == "Block":
            obj = Block(obj_name, pose)
            pose.occupied_by = obj
        else:
            obj = Robot(obj_name, pose)

        states.objects[obj_name] = obj
        states.poses[pose_name] = pose

        idx += 1

    for obj_name, info in goal_config.items():
        pos = info['position']
        pose_name = find_pose_from_value(states.poses, pos)
        if pose_name is None:
            pose_name = str(len(states.poses)+1)
            pose = Pose(pose_name, pos)


        pass

    return states

def find_pose_from_value(poses: Dict[str, Pose], pos: List[float]) -> Optional[str]:
    pose_names = poses.keys()
    pose_coords = [p.position for p in poses.values()]

    if pos not in pose_coords:
        return None

    pose_idx = pose_coords.index(pos)
    pos_name = list(pose_names)[pose_idx]

    return pos_name