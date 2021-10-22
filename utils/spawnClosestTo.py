def spawArround(world, target):
    last_dist = 9999
    final_idx = -1
    for idx, spawnPoint in enumerate(world.get_map().get_spawn_points()):
        if spawnPoint.rotation.yaw > (target.rotation.yaw-25) and spawnPoint.rotation.yaw < (target.rotation.yaw+25):
            if last_dist > target.location.distance(spawnPoint.location):
                last_dist = target.location.distance(spawnPoint.location)
                final_idx = idx
    return world.get_map().get_spawn_points()[final_idx]