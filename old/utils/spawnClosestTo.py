import glob
import os
import sys

try:
    sys.path.append(glob.glob('../../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def spawArround(world, target):
    last_dist = 9999
    final_idx = -1
    for idx, spawnPoint in enumerate(world.get_map().get_spawn_points()):
        if spawnPoint.rotation.yaw > (target.rotation.yaw-25) and spawnPoint.rotation.yaw < (target.rotation.yaw+25):
            if last_dist > target.location.distance(spawnPoint.location):
                last_dist = target.location.distance(spawnPoint.location)
                final_idx = idx
    return world.get_map().get_spawn_points()[final_idx]