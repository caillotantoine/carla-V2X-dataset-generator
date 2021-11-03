import json
from Agent import Agent, Attribute

class Config:

    def __init__(self) -> None:
        self.tps = 1.0/30.0
        self.duration = 15.0
        self.nframe = int(self.duration/self.tps)+1 if self.duration%self.tps > 0.5 else int(self.duration/self.tps)
        self.world = 'Town03'
        self.agents = []

    def read_json(self, path) -> None:
        pass