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
from utils.weatherList import *
from utils.spawnClosestTo import *

weather = weather_lightRain_30deg

V1_t = Transform(Location(x=4.503611, y=30.677336, z=1.495204), Rotation(pitch=3.871590, yaw=-82.755234, roll=-0.000122))
V2_t = Transform(Location(x=1.972299, y=57.928772, z=1.107717), Rotation(pitch=1.554264, yaw=-85.449158, roll=-0.000122))
V3_t = Transform(Location(x=-21.551464, y=7.175428, z=1.506268), Rotation(pitch=0.165127, yaw=54.112213, roll=-0.000122))
sensors_t = Transform(Location(x=0, y=0, z=13.0), Rotation(pitch=-20, yaw=90, roll=0)) # Position of the sensors of the infrastructure
embed_sens_t = Transform(Location(x=0, y=0, z=1.9)) # position of the sensors on the vehicle


synchronous_master = False
nObservers = 4 # 3 cars + 1 infrastructure
tps = nObservers * 0.16 # we plan 0.16 seconds of computation for one observer (3 cam + 1 LiDAR)

def main():

    print('This script does not check the version compatibility between carla and the script. It was developed under the 0.9.11 version. Errors might be expected if ran from another version.')

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # connect to the client
    client = carla.Client('localhost', 2000)    # Parameters of the CARLA server
    client.set_timeout(10.0)                    # Timeout to connect to the server

    
    actor_list = []
    spawn_points = []

    try: 
        # Get the world
        world = client.get_world()

        # Settup the traffic manager
        traffic_manager = client.get_trafficmanager(8000)
        traffic_manager.set_global_distance_to_leading_vehicle(1.0)
        
        # Place the spectator camera (to disable in headless mode)
        spectator = world.get_spectator()
        spectator.set_transform(sensors_t)

        # Find the closest spawn points at the roundabout
        spawn_points.append(spawArround(world, V1_t))         
        spawn_points.append(spawArround(world, V2_t))         
        spawn_points.append(spawArround(world, V3_t))         
        for t in spawn_points:
            print(t)

        # Find the vehicle's blueprints
        blueprint_library = world.get_blueprint_library()
        c3 = blueprint_library.filter('vehicle.citroen.c3')[0]
        model3 = blueprint_library.filter('vehicle.tesla.model3')[0]
        a2 = blueprint_library.filter('vehicle.audi.a2')[0]
        bps = [c3, model3, a2]

        # Setup CARLA wizardry
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        SetVehicleLightState = carla.command.SetVehicleLightState
        FutureActor = carla.command.FutureActor

        # Spawning a batch of vehicles
        batch = []
        for n, transform in enumerate(spawn_points):
            print(n)
            print(bps[n])
            blueprint = bps[n]
            print(blueprint)
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

        # setup the sensor's blueprints

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


        cameraRGB = world.try_spawn_actor(camera_bp, sensors_t)
        if cameraRGB == None:
            print('Failed to spawn the camera RGB')
        else:
            print('Camera RGB spawned')
            print(cameraRGB)
            cameraRGB.listen(lambda image: image.save_to_disk('output/Infra/cameraRGB/%06d.png' % image.frame))
            actor_list.append(cameraRGB.id)

        cameraDepth = world.try_spawn_actor(cameraDepth_bp, sensors_t)
        if cameraRGB == None:
            print('Failed to spawn the camera Depth')
        else:
            print('Camera Depth spawned')
            print(cameraDepth)
            cameraDepth.listen(lambda image: image.save_to_disk('output/Infra/cameraDepth/%06d.png' % image.frame, carla.ColorConverter.LogarithmicDepth))
            actor_list.append(cameraDepth.id)

        cameraSem = world.try_spawn_actor(cameraSem_bp, sensors_t)
        if cameraSem == None:
            print('Failed to spawn the camera Sem')
        else:
            print('Camera Sem spawned')
            print(cameraSem)
            cameraSem.listen(lambda image: image.save_to_disk('output/Infra/cameraSem/%06d.png' % image.frame, carla.ColorConverter.CityScapesPalette))
            actor_list.append(cameraSem.id)
        

        lidarInfra = world.try_spawn_actor(VLP32_bp, Transform(sensors_t.location))
        if lidarInfra == None:
            print('Failed to spawn the LiDAR Infra')
        else:
            print('LiDAR Infra spawned')
            print(lidarInfra)
            lidarInfra.listen(lambda pointcloud: pointcloud.save_to_disk('output/Infra/LiDAR/%06d.ply' % pointcloud.frame))
            actor_list.append(lidarInfra.id)
        
        # Infinite loop to wait the end of the world
        

        V1 = world.get_actor(actor_list[0])
        print('V1 : ')
        print(V1)

        V2 = world.get_actor(actor_list[1])
        print('V2 : ')
        print(V2)

        V3 = world.get_actor(actor_list[2])
        print('V3 : ')
        print(V3)

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




        cameraRGB_emb_V2 = world.try_spawn_actor(camera_bp, embed_sens_t, attach_to=V2, attachment_type=AttachmentType.Rigid)
        if cameraRGB_emb_V2 == None:
            print('Failed to spawn the camera RGB_emb_V2')
        else:
            print('Camera RGB_emb_V2 spawned')
            print(cameraRGB_emb_V2)
            cameraRGB_emb_V2.listen(lambda image: image.save_to_disk('output/Embed/V2/cameraRGB/%06d.png' % image.frame))
            actor_list.append(cameraRGB_emb_V2.id)

        cameraDepth_emb_V2 = world.try_spawn_actor(cameraDepth_bp, embed_sens_t, attach_to=V2, attachment_type=AttachmentType.Rigid)
        if cameraDepth_emb_V2 == None:
            print('Failed to spawn the camera Depth_emb_V2')
        else:
            print('Camera Depth_emb_V2 spawned')
            print(cameraDepth_emb_V2)
            cameraDepth_emb_V2.listen(lambda image: image.save_to_disk('output/Embed/V2/cameraDepth/%06d.png' % image.frame, carla.ColorConverter.LogarithmicDepth))
            actor_list.append(cameraDepth_emb_V2.id)

        cameraSem_emb_V2 = world.try_spawn_actor(cameraSem_bp, embed_sens_t, attach_to=V2, attachment_type=AttachmentType.Rigid)
        if cameraSem_emb_V2 == None:
            print('Failed to spawn the camera Sem_emb_V2')
        else:
            print('Camera Sem_emb_V2 spawned')
            print(cameraSem_emb_V2)
            cameraSem_emb_V2.listen(lambda image: image.save_to_disk('output/Embed/V2/cameraSem/%06d.png' % image.frame, carla.ColorConverter.CityScapesPalette))
            actor_list.append(cameraSem_emb_V2.id)
        

        lidarEmbV2 = world.try_spawn_actor(VLP32_bp, Transform(embed_sens_t.location), attach_to=V2, attachment_type=AttachmentType.Rigid)
        if lidarEmbV2 == None:
            print('Failed to spawn the LiDAR EmbV2')
        else:
            print('LiDAR EmbV2 spawned')
            print(lidarEmbV2)
            lidarEmbV2.listen(lambda pointcloud: pointcloud.save_to_disk('output/Embed/V2/LiDAR/%06d.ply' % pointcloud.frame))
            actor_list.append(lidarEmbV2.id)


        cameraRGB_emb_V3 = world.try_spawn_actor(camera_bp, embed_sens_t, attach_to=V3, attachment_type=AttachmentType.Rigid)
        if cameraRGB_emb_V3 == None:
            print('Failed to spawn the camera RGB_emb_V3')
        else:
            print('Camera RGB_emb_V3 spawned')
            print(cameraRGB_emb_V3)
            cameraRGB_emb_V3.listen(lambda image: image.save_to_disk('output/Embed/V3/cameraRGB/%06d.png' % image.frame))
            actor_list.append(cameraRGB_emb_V3.id)

        cameraDepth_emb_V3 = world.try_spawn_actor(cameraDepth_bp, embed_sens_t, attach_to=V3, attachment_type=AttachmentType.Rigid)
        if cameraDepth_emb_V3 == None:
            print('Failed to spawn the camera Depth_emb_V3')
        else:
            print('Camera Depth_emb_V3 spawned')
            print(cameraDepth_emb_V3)
            cameraDepth_emb_V3.listen(lambda image: image.save_to_disk('output/Embed/V3/cameraDepth/%06d.png' % image.frame, carla.ColorConverter.LogarithmicDepth))
            actor_list.append(cameraDepth_emb_V3.id)

        cameraSem_emb_V3 = world.try_spawn_actor(cameraSem_bp, embed_sens_t, attach_to=V3, attachment_type=AttachmentType.Rigid)
        if cameraSem_emb_V3 == None:
            print('Failed to spawn the camera Sem_emb_V3')
        else:
            print('Camera Sem_emb_V3 spawned')
            print(cameraSem_emb_V3)
            cameraSem_emb_V3.listen(lambda image: image.save_to_disk('output/Embed/V3/cameraSem/%06d.png' % image.frame, carla.ColorConverter.CityScapesPalette))
            actor_list.append(cameraSem_emb_V3.id)
        

        lidarEmbV3 = world.try_spawn_actor(VLP32_bp, Transform(embed_sens_t.location), attach_to=V3, attachment_type=AttachmentType.Rigid)
        if lidarEmbV3 == None:
            print('Failed to spawn the LiDAR EmbV3')
        else:
            print('LiDAR EmbV3 spawned')
            print(lidarEmbV3)
            lidarEmbV3.listen(lambda pointcloud: pointcloud.save_to_disk('output/Embed/V3/LiDAR/%06d.ply' % pointcloud.frame))
            actor_list.append(lidarEmbV3.id)

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
