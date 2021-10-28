import carla
from carla import Transform, Location, Rotation
from carla import VehicleLightState as vls
from tqdm import tqdm
import random
import time
from typing import List

from utils.weatherList import *
from utils.spawnClosestTo import *
from utils.spawnSensors import *
from utils.sensors import *
from utils.Agent import *

TPS = 1.0/30.0
DURATION = 15.0
NFRAME = int(DURATION/TPS)+1 if DURATION%TPS > 0.5 else int(DURATION/TPS)
WORLD = 'Town03'

vehicle_spawn_pts = []
vehicle_spawn_pts.append(Transform(Location(x=4.503611, y=30.677336, z=1.495204), Rotation(pitch=3.871590, yaw=-82.755234, roll=-0.000122)))
vehicle_spawn_pts.append(Transform(Location(x=1.972299, y=57.928772, z=1.107717), Rotation(pitch=1.554264, yaw=-85.449158, roll=-0.000122)))
vehicle_spawn_pts.append(Transform(Location(x=-21.551464, y=7.175428, z=1.506268), Rotation(pitch=0.165127, yaw=54.112213, roll=-0.000122)))
sensors_t = Transform(Location(x=0, y=0, z=13.0), Rotation(pitch=-20, yaw=90, roll=0)) # Position of the sensors of the infrastructure
embed_sens_t = Transform(Location(x=0, y=0, z=1.9)) # position of the sensors on the vehicle


def main():
    print("===========================\n\tSetup....\n===========================")
    print("Number of frames required : {}".format(NFRAME))

    # Connecting to CARLA
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    actor_list = []
    spawn_points = []

    try:
        world = client.get_world()
        world = client.load_world(WORLD) # Setting the world

        spectator = world.get_spectator()
        spectator.set_transform(sensors_t)

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

        v_attrib = Attribute(transform, blueprint, "output/")
        s_attrib = []
        s_attrib.append(Attribute(sensors_t, camera_bp, "output/"))
        agents.append(Agent("vehicle", n, v_attrib, s_attrib))

    
    for agent in agents:
        actor_list = actor_list + agent.spawn(world)
        print(agent.get_actors_list())

    # # Vehicles' sensors
    # V_sensors = []
    # print(actor_list)
    
    # for i in range(len(vehicle_spawn_pts)):
    #     V_sensors.append(spawnSensors(world, actor_list, "output/Embed/V%d"%i, embed_sens_t, world.get_actor(actor_list[i])))

    # # Capteurs de l'infrastructure
    # infra_sensors = spawnSensors(world, actor_list, 'output/Infra', sensors_t, None)
    


    print("===========================\n\tRendering....\n===========================")
    try:
        for _ in tqdm(range(NFRAME)):
            world.tick()
            actors = world.get_actors(actor_list)
            for actor in actors:
                pass
                # print(actor.type_id.find("vehicle") != -1)
            # time.sleep(0.2)
    finally:
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        settings.synchronous_mode = False
        traffic_manager.set_synchronous_mode(False)
        world.apply_settings(settings)
        
    

if __name__ == '__main__':
    main()