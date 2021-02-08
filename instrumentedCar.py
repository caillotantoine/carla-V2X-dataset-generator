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
from carla import VehicleLightState as vls

import argparse
import logging
from carla import Transform, Location, Rotation, AttachmentType
from weatherList import *

weather = weather_lightRain_30deg

synchronous_master = False

def main():

    print('This script does not check the version compatibility between carla and the script. It was developed under the 0.9.11 version. Errors might be expected if ran from another version.')

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


    client = carla.Client('localhost', 2000)    # Parameters of the CARLA server
    client.set_timeout(10.0)                    # Timeout to connect to the server

    print('You are connected to the simulator.')

    embed_sens_t = Transform(Location(x=0, y=0, z=2.0))

    actor_list = []
    spawn_points = []

    try: 
        world = client.get_world()
        traffic_manager = client.get_trafficmanager(8000)
        traffic_manager.set_global_distance_to_leading_vehicle(1.0)

        spawn_points.append(random.choice(world.get_map().get_spawn_points()))         
        print(spawn_points[0])

        blueprint_library = world.get_blueprint_library()
        bps = []
        bps.append(blueprint_library.filter('vehicle.citroen.c3')[0])

        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        SetVehicleLightState = carla.command.SetVehicleLightState
        FutureActor = carla.command.FutureActor

        batch = []
        for n, transform in enumerate(spawn_points):
            blueprint = bps[n]
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            blueprint.set_attribute('role_name', 'autopilot')

            # prepare the light state of the cars to spawn
            light_state = vls.NONE

            # spawn the cars and set their autopilot and light state all together
            batch.append(SpawnActor(blueprint, transform)
                .then(SetAutopilot(FutureActor, True, traffic_manager.get_port()))
                .then(SetVehicleLightState(FutureActor, light_state)))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                actor_list.append(response.actor_id)

        camera_bp = blueprint_library.find('sensor.camera.rgb')
        # camera_bp.set_attribute('image_size_x', '1920')
        # camera_bp.set_attribute('image_size_y', '1080')
        # camera_bp.set_attribute('fov', '110')
        camera_bp.set_attribute('sensor_tick', '0.05')

        cameraDepth_bp = blueprint_library.find('sensor.camera.depth')
        # cameraDepth_bp.set_attribute('image_size_x', '1920')
        # cameraDepth_bp.set_attribute('image_size_y', '1080')
        # cameraDepth_bp.set_attribute('fov', '110')
        cameraDepth_bp.set_attribute('sensor_tick', '0.05')

        cameraSem_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
        # cameraSem_bp.set_attribute('image_size_x', '1920')
        # cameraSem_bp.set_attribute('image_size_y', '1080')
        # cameraSem_bp.set_attribute('fov', '110')
        cameraSem_bp.set_attribute('sensor_tick', '0.05')

        VLP32_bp = blueprint_library.find('sensor.lidar.ray_cast')
        VLP32_bp.set_attribute('rotation_frequency','20')
        VLP32_bp.set_attribute('channels','32')
        VLP32_bp.set_attribute('points_per_second','1200000')
        VLP32_bp.set_attribute('range','200.0')
        VLP32_bp.set_attribute('upper_fov','15.0')
        VLP32_bp.set_attribute('lower_fov','-25.0')
        
        # Infinite loop to wait the end of the world
        

        V1 = world.get_actor(actor_list[0])
        print('V1 : ')
        print(V1)

        cameraRGB_emb_V1 = world.try_spawn_actor(camera_bp, embed_sens_t, attach_to=V1, attachment_type=AttachmentType.Rigid)
        if cameraRGB_emb_V1 == None:
            print('Failed to spawn the camera RGB_emb_V1')
        else:
            print('Camera RGB_emb_V1 spawned')
            print(cameraRGB_emb_V1)
            cameraRGB_emb_V1.listen(lambda image: image.save_to_disk('output/Embed/V1/cameraRGB/%06d.png' % image.frame))
            actor_list.append(cameraRGB_emb_V1.id)

        cameraDepth_emb_V1 = world.try_spawn_actor(cameraDepth_bp, embed_sens_t, attach_to=V1, attachment_type=AttachmentType.Rigid)
        if cameraDepth_emb_V1 == None:
            print('Failed to spawn the camera Depth_emb_V1')
        else:
            print('Camera Depth_emb_V1 spawned')
            print(cameraDepth_emb_V1)
            cameraDepth_emb_V1.listen(lambda image: image.save_to_disk('output/Embed/V1/cameraDepth/%06d.png' % image.frame, carla.ColorConverter.LogarithmicDepth))
            actor_list.append(cameraDepth_emb_V1.id)

        cameraSem_emb_V1 = world.try_spawn_actor(cameraSem_bp, embed_sens_t, attach_to=V1, attachment_type=AttachmentType.Rigid)
        if cameraSem_emb_V1 == None:
            print('Failed to spawn the camera Sem_emb_V1')
        else:
            print('Camera Sem_emb_V1 spawned')
            print(cameraSem_emb_V1)
            cameraSem_emb_V1.listen(lambda image: image.save_to_disk('output/Embed/V1/cameraSem/%06d.png' % image.frame, carla.ColorConverter.CityScapesPalette))
            actor_list.append(cameraSem_emb_V1.id)
        

        lidarEmbV1 = world.try_spawn_actor(VLP32_bp, Transform(embed_sens_t.location), attach_to=V1, attachment_type=AttachmentType.Rigid)
        if lidarEmbV1 == None:
            print('Failed to spawn the LiDAR EmbV1')
        else:
            print('LiDAR EmbV1 spawned')
            print(lidarEmbV1)
            lidarEmbV1.listen(lambda pointcloud: pointcloud.save_to_disk('output/Embed/V1/LiDAR/%06d.ply' % pointcloud.frame))
            actor_list.append(lidarEmbV1.id)

        print('Press Ctrl + C to quit')
        while True:
                # print(V1.get_transform())
                #spectator.set_transform(V1.get_transform())
                world.wait_for_tick()

    finally:
        print('Destroying Actors')
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('Actors destroyed')

    
if __name__ == '__main__':
    main()
