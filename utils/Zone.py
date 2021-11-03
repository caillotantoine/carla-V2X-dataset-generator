import math
import carla
from carla import Transform, Location, Rotation
from typing import Any, List
import random

class Zone:
    def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float) -> None:
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def is_in_zone(self, point: Transform) -> bool:
        L = point.location
        if (L.x >= self.x_min) and (L.x <= self.x_max) and (L.y >= self.y_min) and (L.y <= self.y_max):
            return True
        return False

    def get_spawnpoints(self, world:carla.World, all=False) -> List[Transform]:
        raw_sp_pts = world.get_map().get_spawn_points()
        if all:
            return raw_sp_pts
        spawn_points:List[Transform] = []
        for point in raw_sp_pts:
            if self.is_in_zone(point):
                spawn_points.append(point)
        return spawn_points

    def get_Nrandom_spawnpoints(self,world:carla.World, N: int, all=False) -> List[Transform]:
        points_in_zone = self.get_spawnpoints(world, all=all)
        random.shuffle(points_in_zone)
        return points_in_zone[:N]

    def get_closest_spawnpoint(self, world:carla.World, point:Transform, sim_yaw=False, all=False) -> Transform:
        spwn_pts = self.get_spawnpoints(world, all=all)
        dist: float = math.inf
        point_out:Transform = None
        for sp in spwn_pts:
            if (not sim_yaw) or ((sp.rotation.yaw > (point.rotation.yaw-25)) and (sp.rotation.yaw < (point.rotation.yaw+25))):     # with a similar yaw?
                if dist > point.location.distance(sp.location):
                    dist = point.location.distance(sp.location)
                    point_out = sp
        return point_out