import carla

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

ROI = Zone(0, 0, 0, 0)


def main():
    print("===========================\n\tSetup....\n===========================")
    print("Number of frames required : {}".format(NFRAME))

    # Connecting to CARLA
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    actor_list = []
    

    try:
        world = client.get_world()
        world = client.load_world(WORLD) # Setting the world

        # spectator = world.get_spectator()
        # spectator.set_transform(infra_spawn_pts[0])

        traffic_manager = client.get_trafficmanager()

        # Setting up the simulation in synchronous mode
        settings = world.get_settings()
        settings.fixed_delta_seconds = TPS
        settings.synchronous_mode = False
        traffic_manager.set_synchronous_mode(False)

        world.apply_settings(settings)
        blueprint_library = world.get_blueprint_library()


    except Exception as e:
        print("Setting up world failled.\n{}".format(e))
        exit()

    print("===========================\n\tRendering....\n===========================")
    try:
        while(True):
            world.wait_for_tick()
            action = input("What to do (c: car, p: pedestrian, i: infra, a: any, u: undo): ")
            spectator = world.get_spectator()
            loc = spectator.get_transform()
            print(loc)
            if action == 'a' or action == 'i':
                print(loc)
            if action == "c":
                vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))
                spawn = ROI.get_closest_spawnpoint(world, loc, all=True, sim_yaw=True)
                print(f"Chose loc : {spawn}")
                try:
                    actor = world.spawn_actor(vehicle_bp, spawn)
                    actor_list.append(actor)
                except Exception as e:
                    print(f"Error spawning vehicle {e}")
            
            if action == "p":
                vehicle_bp = random.choice(blueprint_library.filter('walker.*.*'))
                # spawn = ROI.get_closest_spawnpoint(world, loc, all=True, sim_yaw=False)
                # print(f"Chose loc : {spawn}")
                try:
                    actor = world.spawn_actor(vehicle_bp, loc)
                    actor_list.append(actor)
                except Exception as e:

                    print(f"Error spawning vehicle {e}")

            if action == "u":
                actor = actor_list.pop()
                actor.destroy()

    

    finally:
        client.apply_batch([carla.command.DestroyActor(x.id) for x in actor_list])
        settings.synchronous_mode = False
        traffic_manager.set_synchronous_mode(False)
        world.apply_settings(settings)
        
    

if __name__ == '__main__':
    main()