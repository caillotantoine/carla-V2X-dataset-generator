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
    print("Number of frames required : {}".format(NFRAME))

    # Connecting to CARLA
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    actor_list = []
    spawn_points = []
    output_queue = queue.Queue()
    FIRST_hjvgckfhxddts = True

    ROI = Zone(-120.0, 120.0, -120.0, 120.0)
    # print(ROI.is_in_zone(vehicle_spawn_pts[0]))
    

    try:
        world = client.get_world()
        world = client.load_world(WORLD) # Setting the world

        spectator = world.get_spectator()
        spectator.set_transform(infra_spawn_pts[0])

        traffic_manager = client.get_trafficmanager()

        # Setting up the simulation in synchronous mode
        settings = world.get_settings()
        settings.fixed_delta_seconds = TPS
        settings.synchronous_mode = True
        traffic_manager.set_synchronous_mode(True)

        world.apply_settings(settings)


    except Exception as e:
        print("Setting up world failled.\n{}".format(e))
        exit()

    print(ROI.get_Nrandom_spawnpoints(world, 10))

    for v_spwn_pt in vehicle_spawn_pts:
        spawn_points.append(ROI.get_closest_spawnpoint(world, v_spwn_pt))
    for t in spawn_points:
        print(t)

    # Find the vehicle's blueprints
    blueprint_library = world.get_blueprint_library()
    c3 = blueprint_library.filter('vehicle.citroen.c3')[0]
    model3 = blueprint_library.filter('vehicle.tesla.model3')[0]
    a2 = blueprint_library.filter('vehicle.audi.a2')[0]
    bps = [c3, model3, a2]

    agents:list[Agent] = []
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

        camera_bp = get_KITTIcam_bp(blueprint_library)
        cameraSem_bp = get_KITTIcamSem_bp(blueprint_library)

        v_attrib = Attribute(transform, blueprint, "output/V%03d/"%n)
        s_attrib = []
        s_attrib.append(Attribute(embed_sens_t, camera_bp, "output/V%03d/"%n))
        s_attrib.append(Attribute(embed_sens_t, cameraSem_bp, "output/V%03d/"%n))
        agents.append(Agent("vehicle", n, "output/V%03d/"%n, v_attrib, s_attrib))

    for n, transform in enumerate(infra_spawn_pts):
        camera_bp = get_KITTIcam_bp(blueprint_library)
        cameraSem_bp = get_KITTIcamSem_bp(blueprint_library)
        s_attrib = []
        s_attrib.append(Attribute(transform, camera_bp, "output/I%03d/"%n))
        s_attrib.append(Attribute(transform, cameraSem_bp, "output/I%03d/"%n))
        agents.append(Agent("infrastructure", n, "output/I%03d/"%n, sensors=s_attrib))

    for n, transform in enumerate(pedestrian_spawn_pts):
        walker_bp = random.choice(blueprint_library.filter('walker.*.*'))
        walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
        if walker_bp.has_attribute('is_invincible'):
            walker_bp.set_attribute('is_invincible', 'false')
        if walker_bp.has_attribute('speed'):
            walker_speed = walker_bp.get_attribute('speed').recommended_values[1]
        else:
            walker_speed = 0.0
        v_attrib = Attribute(transform, walker_bp, "output/P%03d/"%n)
        s_attrib = []
        s_attrib.append(Attribute(Transform(), walker_controller_bp, "output/P%03d/"%n, maxspeed=walker_speed))
        agents.append(Agent("pedestrian", n, "output/P%03d/"%n, vehicle=v_attrib, sensors=s_attrib))
    
    for agent in agents:
        actor_list = actor_list + agent.spawn(world, output_queue)
        print(agent.get_actors_list())

    print("===========================\n\tRendering....\n===========================")
    try:
        for frame in tqdm(range(NFRAME)):
            # actors = world.get_actors(actor_list)

            # print("Queue size : {}, empty : {}".format(output_queue.qsize(), output_queue.empty()))
            snapshots = []
            while not output_queue.empty():
                snapshots.append(output_queue.get(True))

            world.tick()
            
            if FIRST_hjvgckfhxddts:
                FIRST_hjvgckfhxddts = False
                time.sleep(2)

            for (attrib, data) in snapshots:
                attrib.save(data, frame)

            for agent in agents:
                agent.save_status(world, frame=frame)

                # (attrib, data) = output_queue.clear()
            #     attrib.save(data, frame)
            # time.sleep(0.2)
    except Exception as e:
        print(f"Error {e}")
    finally:
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        settings.synchronous_mode = False
        traffic_manager.set_synchronous_mode(False)
        world.apply_settings(settings)
        
    

if __name__ == '__main__':
    main()