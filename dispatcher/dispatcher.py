from typing import List, Dict
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

        self.entity_dict = {"block": "cube.urdf", "robot": "r2d2.urdf"}
        self.entity_ids = []

        self.physicsClient = p.connect(p.GUI)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")

    def initialize_objects(self) -> None:
        for pred in self.init_predicates:
            if pred.name == "at":
                obj = pred.terms[0].name.split("_")[0]
                self.objects.append(obj)
                pos_name = pred.terms[1].name
                pos = self.positions[pos_name]
                pos[-1] += 0.4

                entity_id = p.loadURDF(self.entity_dict[obj], pos, self.default_orientation)
                self.entity_ids.append(entity_id)

    def run_simulation(self, duration: int = 0) -> None:
        for entity in self.entity_ids:
            pos, orn = p.getBasePositionAndOrientation(entity)
            print(self.objects[entity-1], pos, orn)

        if duration == 0:
            while(True):
                p.stepSimulation()
                time.sleep(1./240.)
        else:
            for _ in range(duration):
                p.stepSimulation()
                time.sleep(1./240.)

        p.disconnect()

    @staticmethod
    def execute_command(command: str, args: List[str]):
        match command:
            case "move":
                move_action(args)
            case "grasp":
                grasp_action(args)
            case "place":
                place_action(args)
            case _:
                print(f"Unknown command: {command}")

def move_action(args: List[str]):
    print(f"Move action executed with args: {args}")

def grasp_action(args: List[str]):
    print(f"Grasp action executed with args: {args}")

def place_action(args: List[str]):
    print(f"Place action executed with args: {args}")
