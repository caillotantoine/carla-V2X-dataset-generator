import json
from Agent import Agent, Attribute
import carla
from carla import Transform, Location, Rotation
from typing import Any, List

class Config:

    def __init__(self) -> None:
        self.tps = 1.0/30.0
        self.duration = 15.0
        self.nframe = int(self.duration/self.tps)+1 if self.duration%self.tps > 0.5 else int(self.duration/self.tps)
        self.world = 'Town03'
        self.agents = []
        self.agents_description = []

    def read_json(self, path) -> None:
        pass