import glob
import os
import sys

# Import CARLA from the egg
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
from utils.sensors import *

def spawnSensors(world, actor_list, path, transform, parent=None):
    blueprint_library = world.get_blueprint_library()

    camera_bp = get_camera_bp(blueprint_library)
    cameraDepth_bp = get_cameraDepth_bp(blueprint_library)
    cameraSem_bp = get_cameraSem_bp(blueprint_library)
    VLP32_bp = get_VLP32_bp(blueprint_library)

    if(parent == None):
        camRGB  = world.try_spawn_actor(camera_bp, transform)
        camDepth  = world.try_spawn_actor(cameraDepth_bp, transform)
        camSem  = world.try_spawn_actor(cameraSem_bp, transform)
        LiDAR = world.try_spawn_actor(VLP32_bp, carla.Transform(transform.location))
    else:
        camRGB  = world.try_spawn_actor(camera_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        camDepth  = world.try_spawn_actor(cameraDepth_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        camSem  = world.try_spawn_actor(cameraSem_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        LiDAR = world.try_spawn_actor(VLP32_bp, carla.Transform(transform.location), attach_to=parent, attachment_type=carla.AttachmentType.Rigid)

    if camRGB == None:
        print('Failed to spawn the camera RGB')
    else:
        camRGB.listen(lambda image: image.save_to_disk('%s/cameraRGB/%06d.png' % (path, image.frame)))
        actor_list.append(camRGB.id)

    if camDepth == None:
        print('Failed to spawn the camera Depth')
    else:
        camDepth.listen(lambda image: image.save_to_disk('%s/cameraDepth/%06d.png' % (path, image.frame), carla.ColorConverter.LogarithmicDepth))
        actor_list.append(camDepth.id)

    if camSem == None:
        print('Failed to spawn the camera Sem')
    else:
        camSem.listen(lambda image: image.save_to_disk('%s/cameraSem/%06d.png' % (path, image.frame), carla.ColorConverter.CityScapesPalette))
        actor_list.append(camSem.id)

    if LiDAR == None:
        print('Failed to spawn the LiDAR')
    else:
        LiDAR.listen(lambda pointcloud: pointcloud.save_to_disk('%s/LiDAR/%06d.png' % (path, pointcloud.frame)))
        actor_list.append(LiDAR.id)
    

    return (camRGB, camDepth, camSem, LiDAR)

