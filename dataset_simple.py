import glob
import os
import sys
import time

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
from utils.spawnSensors import *
from utils.sensors import *

weather = weather_clear_noon

vehicle_spawn_pts = []
vehicle_spawn_pts.append(Transform(Location(x=4.503611, y=30.677336, z=1.495204), Rotation(pitch=3.871590, yaw=-82.755234, roll=-0.000122)))
vehicle_spawn_pts.append(Transform(Location(x=1.972299, y=57.928772, z=1.107717), Rotation(pitch=1.554264, yaw=-85.449158, roll=-0.000122)))
vehicle_spawn_pts.append(Transform(Location(x=-21.551464, y=7.175428, z=1.506268), Rotation(pitch=0.165127, yaw=54.112213, roll=-0.000122)))
sensors_t = Transform(Location(x=0, y=0, z=13.0), Rotation(pitch=-20, yaw=90, roll=0)) # Position of the sensors of the infrastructure
embed_sens_t = Transform(Location(x=0, y=0, z=1.9)) # position of the sensors on the vehicle

print(sensors_t.get_matrix())

nObservers = 4 # 3 cars + 1 infrastructure
tps = nObservers * 0.8 # we plan 0.3 seconds of computation for one observer (3 cam + 1 LiDAR + fichiers txt)
ips = 20.0

def main():

    print('This script does not check the version compatibility between carla and the script. It was developed under the 0.9.11 version. Errors might be expected if ran from another version.')

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # connect to the client
    client = carla.Client('localhost', 2000)    # Parameters of the CARLA server
    client.set_timeout(10.0)                    # Timeout to connect to the server

    
    actor_list = []
    spawn_points = []

    synchronous_master = False
    try: 
        # Get the world
        world = client.get_world()
        world.set_weather(weather)

        # Settup the traffic manager
        traffic_manager = client.get_trafficmanager(8000)
        traffic_manager.set_global_distance_to_leading_vehicle(1.0)

        settings = world.get_settings()
        
        # Setting up the synchronous mode
        traffic_manager.set_synchronous_mode(True)
        if not settings.synchronous_mode:
            synchronous_master = True
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 1.0/ips
            print("Synchronous mode activated")
        else:
            synchronous_master = False
            print("Already in synchronous mode")
        world.apply_settings(settings)
        
        # Place the spectator camera (to disable in headless mode)
        spectator = world.get_spectator()
        spectator.set_transform(sensors_t)

        # Find the closest spawn points at the roundabout
        for v_spwn_pt in vehicle_spawn_pts:
            spawn_points.append(spawArround(world, v_spwn_pt))

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

        # Capteus des vehicules
        V_sensors = []
        print(actor_list)
        for i in range(len(vehicle_spawn_pts)):
            V_sensors.append(spawnSensors(world, actor_list, "output/Embed/V%d"%i, embed_sens_t, world.get_actor(actor_list[i])))

        # Capteurs de l'infrastructure
        infra_sensors = spawnSensors(world, actor_list, 'output/Infra', sensors_t, None)
        
        # Infinite loop to wait the end of the world
        print('Press Ctrl + C to quit')
        time_computed = 0.0
        while True:
                # print(V1.get_transform())
                #spectator.set_transform(V1.get_transform())
                if synchronous_master:
                    world.tick()
                    time.sleep(tps)
                    time_computed = time_computed + (1.0/ips)
                    print("Seconds computed : %f" % time_computed)
                else:
                    world.wait_for_tick()

    finally:
        print('Destroying Actors')
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('Actors destroyed')

    
if __name__ == '__main__':
    main()
