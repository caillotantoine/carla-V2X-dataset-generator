import carla
from carla import Transform

class Agent:

    def __init__(self):
        pass


class Attribute:
    def __init__(self, pose: Transform, bp, save_path, save_func):
        self.pose = pose
        self.bp = bp
        self.save_path = save_path
        self.save_func = save_func

