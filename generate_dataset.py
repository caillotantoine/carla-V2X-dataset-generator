import math
from os import environ, error
import carla
from carla import Transform, Location, Rotation
from carla import VehicleLightState as vls
from tqdm import tqdm
import random
import time
import queue
from typing import Any, List
from utils.Config import Config

from utils.weatherList import *
from utils.spawnClosestTo import *
from utils.spawnSensors import *
from utils.sensors import *
from utils.Agent import *
from utils.Zone import *

TPS = 1.0/30.0
DURATION = 15.0
NFRAME = int(DURATION/TPS)+1 if DURATION%TPS > 0.5 else int(DURATION/TPS)
WORLD = 'Town03'


vehicle_spawn_pts = []
embed_sens_t = Transform(Location(x=0, y=0, z=1.9)) # position of the sensors on the vehicle
vehicle_spawn_pts.append(Transform(Location(x=4.503611, y=30.677336, z=1.495204), Rotation(pitch=3.871590, yaw=-82.755234, roll=-0.000122)))
vehicle_spawn_pts.append(Transform(Location(x=1.972299, y=57.928772, z=1.107717), Rotation(pitch=1.554264, yaw=-85.449158, roll=-0.000122)))
vehicle_spawn_pts.append(Transform(Location(x=-21.551464, y=7.175428, z=1.506268), Rotation(pitch=0.165127, yaw=54.112213, roll=-0.000122)))

pedestrian_spawn_pts = []
pedestrian_spawn_pts.append(Transform(Location(x=-18.057878, y=32.290249, z=2.474842), Rotation(pitch=1.811482, yaw=90.618484, roll=0.000001)))

infra_spawn_pts = [] # Position of the sensors of the infrastructure
infra_spawn_pts.append(Transform(Location(x=0, y=0, z=13.0), Rotation(pitch=-20, yaw=90, roll=0)))


def main():
    print("===========================\n\tSetup....\n===========================")

    # Connecting to CARLA
    client = carla.Client('localhost', 2000)
    client.set_timeout(30.0)

    actor_list = []
    spawn_points = []
    output_queue = queue.Queue()
    FIRST_hjvgckfhxddts = True

    configurator = Config()
    configurator.read_json('./config/scenario_oclusion.json')
    (world, settings, traffic_manager) = configurator.setup_world(client=client)
    configurator.create_agents(world)
    print(configurator)
    actor_list = configurator.spawn_actors(world, output_queue)


    print("===========================\n\tRendering....\n===========================")
    try:
        for frame in tqdm(range(configurator.get_nframes())):
            snapshots = []
            while not output_queue.empty():
                snapshots.append(output_queue.get(True))

            world.tick()
            
            if FIRST_hjvgckfhxddts:
                FIRST_hjvgckfhxddts = False
                time.sleep(2)

            for (attrib, data) in snapshots:
                attrib.save(data, frame)

            for agent in configurator.get_agents():
                agent.save_status(world, frame=frame)

    except Exception as e:
        print(f"Error {e}")
    finally:
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        settings.synchronous_mode = False
        traffic_manager.set_synchronous_mode(False)
        world.apply_settings(settings)
        
    

if __name__ == '__main__':
    main()