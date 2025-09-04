from typing import List, Dict, Tuple
from itertools import cycle
from pddl.logic import Constant, Predicate

import pybullet as p
import time
import pybullet_data

class CommandDispatcher:
    def __init__(self, init_predicates: List[Predicate], positions: Dict[str, List[float]]) -> None:
        self.objects = []
        self.init_predicates = init_predicates
        self.positions = positions
        self.default_orientation = p.getQuaternionFromEuler([0.0, 0.0, 0.0])

        self.entity_urdf_dict = {"block": "cube.urdf", "robot": "r2d2.urdf"}
        self.object_entity_dict = {}
        self.entity_ids = []

        self.physicsClient = p.connect(p.GUI)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")

        self.robot_wheel_joints = {2: 'right_front_wheel_joint',
                                   3: 'right_back_wheel_joint',
                                   6: 'left_front_wheel_joint',
                                   7: 'left_back_wheel_joints'}

    def initialize_objects(self) -> None:
        for pred in self.init_predicates:
            if pred.name == "at":
                obj = pred.terms[0].name
                self.objects.append(obj)
                pos_name = pred.terms[1].name
                pos = self.positions[pos_name]
                pos[-1] += 0.5

                urdf_key = obj.split("_")[0]
                entity_id = p.loadURDF(self.entity_urdf_dict[urdf_key], pos, self.default_orientation)
                self.entity_ids.append(entity_id)
                self.object_entity_dict[obj] = entity_id

    def run_simulation(self, commands: List[Tuple[str, List[str]]], duration: int = 0) -> None:
        for entity in self.entity_ids:
            pos, orn = p.getBasePositionAndOrientation(entity)
            print(self.objects[entity-1], pos, orn)

        time.sleep(2.0)

        rob_entity_id = self.object_entity_dict["robot"]

        cmd_index = 0
        if duration == 0:
            while(True):
                if cmd_index < len(commands):
                    cmd, args = commands[cmd_index]
                    self.execute_command(cmd, args)
                cmd_index += 1

                # mode = p.VELOCITY_CONTROL
                # p.setJointMotorControlArray(rob_entity_id, jointIndices=[2, 3, 6, 7], controlMode=mode, targetVelocities=[10.0, 10.0, 10.0, 10.0])

                p.stepSimulation()
                time.sleep(1./240.)
        else:
            for _ in range(duration):
                if cmd_index < len(commands):
                    cmd, args = commands[cmd_index]
                    self.execute_command(cmd, args)
                cmd_index += 1

                p.stepSimulation()
                time.sleep(1./240.)

        p.disconnect()

    def execute_command(self, command: str, args: List[str]):
        match command:
            case "move":
                self.move_action(args)
            case "grasp":
                self.grasp_action(args)
            case "place":
                self.place_action(args)
            case _:
                print(f"Unknown command: {command}")

    def move_action(self, args: List[str]):
        # print(f"Move action executed with args: {args}")
        entity_id = self.object_entity_dict[args[0]]
        target_pos = self.positions[args[2]]
        target_pos[0] += 1.2
        target_pos[2] = 0.4

        p.removeBody(entity_id)
        new_entity_id = p.loadURDF(self.entity_urdf_dict[args[0]], target_pos, self.default_orientation)
        self.entity_ids.append(new_entity_id)
        self.entity_ids.remove(entity_id)
        self.object_entity_dict[args[0]] = new_entity_id

    def grasp_action(self, args: List[str]):
        # print(f"Grasp action executed with args: {args}")
        entity_id = self.object_entity_dict[args[1]]
        p.removeBody(entity_id)
        self.entity_ids.remove(entity_id)

    def place_action(self, args: List[str]):
        # print(f"Place action executed with args: {args}")
        pos = self.positions[args[2]]
        place_pos = pos
        place_pos[0] += 1.2
        place_pos[2] = 0.5

        urdf_key = args[1].split("_")[0]
        entity_id = p.loadURDF(self.entity_urdf_dict[urdf_key], place_pos, self.default_orientation)
        self.entity_ids.append(entity_id)
        self.object_entity_dict[args[1]] = entity_id
