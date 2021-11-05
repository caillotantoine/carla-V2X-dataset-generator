import json

from tqdm.std import trange
from Agent import Agent, Attribute
import carla
from carla import Transform, Location, Rotation
from typing import Any, List

if __name__ == '__main__':
    from weatherList import *
    from spawnClosestTo import *
    from spawnSensors import *
    from sensors import *
    from Agent import *
    from Zone import *
else:
    from utils.weatherList import *
    from utils.spawnClosestTo import *
    from utils.spawnSensors import *
    from utils.sensors import *
    from utils.Agent import *
    from utils.Zone import *

embed_sens_t = Transform(Location(x=0, y=0, z=1.9)) # position of the sensors on

class Config:
    def __init__(self, crossingWalker:float=30.0, zone:Zone=Zone(-120.0, 120.0, -120.0, 120.0)) -> None:
        self.tps = 1.0/30.0
        self.duration = 15.0
        self.nframe = int(self.duration/self.tps)+1 if self.duration%self.tps > 0.5 else int(self.duration/self.tps)
        self.world = 'Town03'
        self.agents = []
        self.agents_des = []
        self.crossingWalker = crossingWalker
        self.ROI = zone

    def __str__(self):
        out:str = f"Config\n\ttps: {self.tps}\n\tduration: {self.duration}\n\tnframes: {self.nframe}\n\tworld: {self.world}\n\tAgents :\n"
        for n,a in enumerate(self.agents_des):
            out = out + f"\t  {n:03} \t{a[0]}: {a[1]}\t {a[2]}\n"
        return out

    def read_json(self, path) -> None:
        f = open(path, "r")
        data = json.load(f)
        f.close()
        self.tps:float = data["tps"]
        self.duration: float = data["duration"]
        self.nframe = int(self.duration/self.tps)+1 if self.duration%self.tps > 0.5 else int(self.duration/self.tps)
        self.world = data["world"]
        agents_description = data["agents"]

        for agent_des in agents_description:
            loc = agent_des["position"]["location"]
            rot = agent_des["position"]["rotation"]
            L = Location(x=loc["x"], y=loc["y"], z=loc["z"])
            R = Rotation(pitch=rot["pitch"], yaw=rot["yaw"], roll=rot["roll"])
            transform = Transform(L, R)
            bp = agent_des["blueprint"]
            if bp != None:
                bp = bp["id"]
            atype = agent_des["type"]
            self.agents_des.append((atype, bp, transform))

            

    def setup_world(self, client):
        world = client.get_world()
        world = client.load_world(self.world) # Setting the world

        traffic_manager = client.get_trafficmanager()
        settings = world.get_settings()
        settings.fixed_delta_seconds = self.tps
        settings.synchronous_mode = True
        traffic_manager.set_synchronous_mode(True)
        world.apply_settings(settings)
        return world
            

    def create_agents(self, world):
        blueprint_library = world.get_blueprint_library()
        n_infra = 0
        n_vehicle = 0
        n_walker = 0

        camera_bp = get_KITTIcam_bp(blueprint_library)
        cameraSem_bp = get_KITTIcamSem_bp(blueprint_library)

        for agent_des in self.agents_des:
            atype = agent_des[0]
            bp = agent_des[1]
            transform = agent_des[2]

            if atype == "infrastructure":
                s_attrib = []
                s_attrib.append(Attribute(transform, camera_bp, "output/I%03d/"%n_infra))
                s_attrib.append(Attribute(transform, cameraSem_bp, "output/I%03d/"%n_infra))
                self.agents.append(Agent("infrastructure", n_infra, "output/I%03d/"%n_infra, sensors=s_attrib))
                n_infra = n_infra+1


            if atype == "pedestrian":
                walker_bp = blueprint_library.filter(bp)
                walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
                if walker_bp.has_attribute('is_invincible'):
                    walker_bp.set_attribute('is_invincible', 'false')
                if walker_bp.has_attribute('speed'):
                    walker_speed = walker_bp.get_attribute('speed').recommended_values[1]
                else:
                    walker_speed = 0.0
                v_attrib = Attribute(transform, walker_bp, "output/P%03d/"%n_walker)
                s_attrib = []
                s_attrib.append(Attribute(Transform(), walker_controller_bp, "output/P%03d/"%n_walker, maxspeed=walker_speed))
                self.agents.append(Agent("pedestrian", n_walker, "output/P%03d/"%n_walker, vehicle=v_attrib, sensors=s_attrib))
                n_walker = n_walker+1


            if atype == "vehicle":
                blueprint = blueprint_library.filter(bp)
                print(blueprint)
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                blueprint.set_attribute('role_name', 'autopilot')
                v_attrib = Attribute(transform, blueprint, "output/V%03d/"%n_vehicle)
                s_attrib = []
                s_attrib.append(Attribute(embed_sens_t, camera_bp, "output/V%03d/"%n_vehicle))
                s_attrib.append(Attribute(embed_sens_t, cameraSem_bp, "output/V%03d/"%n_vehicle))
                self.agents.append(Agent("vehicle", n_vehicle, "output/V%03d/"%n_vehicle, v_attrib, s_attrib))
                n_vehicle=n_vehicle+1

    def spawn_actors(self, world, queue):
        self.actor_list = []
        for agent in self.agents:
            self.actor_list = self.actor_list + agent.spawn(world, queue)
            print(agent.get_actors_list())
        return self.actor_list

    def get_agents(self):
        return self.agents
                

if __name__ == '__main__':
    config = Config()
    config.read_json("./config/test2.json")
    print(config)