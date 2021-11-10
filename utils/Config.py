import json
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
embed_high_sens_t = Transform(Location(x=0, y=0, z=2.9)) # position of the sensors on

class Config:
    def __init__(self, path: str = "output", crossingWalker:float=30.0, zone:Zone=Zone(-120.0, 120.0, -120.0, 120.0)) -> None:
        self.tps = 1.0/30.0
        self.duration = 15.0
        self.nframe = int(self.duration/self.tps)+1 if self.duration%self.tps > 0.5 else int(self.duration/self.tps)
        self.world = 'Town03'
        self.agents = []
        self.agents_des = []
        self.crossingWalker = crossingWalker
        self.ROI = zone
        self.path = path

    def __str__(self):
        out:str = f"Config\n\ttps: {self.tps}\n\tduration: {self.duration}\n\tnframes: {self.nframe}\n\tworld: {self.world}\n\tcrossing walkers: {self.crossingWalker}\n\tAgents :\n"
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
        return (world, settings, traffic_manager)
            

    def create_agents(self, world):
        blueprint_library = world.get_blueprint_library()
        n_infra = 0
        n_vehicle = 0
        n_walker = 0

        camera_bp = get_KITTIcam_bp(blueprint_library)
        cameraSem_bp = get_KITTIcamSem_bp(blueprint_library)

        oxts = []

        for agent_des in self.agents_des:
            atype = agent_des[0]
            bp = agent_des[1]
            transform = agent_des[2]

            if atype == "infrastructure":
                out_path = "%s/I%03d/"%(self.path, n_infra)
                s_attrib = []
                s_attrib.append(Attribute(transform, camera_bp))
                s_attrib.append(Attribute(transform, cameraSem_bp))
                self.agents.append(Agent("infrastructure", n_infra, out_path, sensors=s_attrib))
                n_infra = n_infra+1

            elif atype == "pedestrian":
                out_path = "%s/P%03d/"%(self.path, n_walker)
                walker_bp = blueprint_library.filter(bp)[0]
                walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
                if walker_bp.has_attribute('is_invincible'):
                    walker_bp.set_attribute('is_invincible', 'false')
                if walker_bp.has_attribute('speed'):
                    walker_speed = walker_bp.get_attribute('speed').recommended_values[1]
                else:
                    walker_speed = 0.0
                v_attrib = Attribute(transform, walker_bp)
                s_attrib = []
                s_attrib.append(Attribute(Transform(), walker_controller_bp, maxspeed=walker_speed))
                self.agents.append(Agent("pedestrian", n_walker, out_path, vehicle=v_attrib, sensors=s_attrib))
                n_walker = n_walker+1

            elif atype == "vehicle":
                out_path = "%s/V%03d/"%(self.path, n_vehicle)
                blueprint = blueprint_library.filter(bp)[0]
                print(blueprint)
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                blueprint.set_attribute('role_name', 'autopilot')
                v_attrib = Attribute(transform, blueprint)
                s_attrib = []
                if bp.split('.')[2] == "carlacola" or bp.split('.')[2] == "ambulance":
                    s_attrib.append(Attribute(embed_high_sens_t, camera_bp))
                    s_attrib.append(Attribute(embed_high_sens_t, cameraSem_bp))
                else:
                    s_attrib.append(Attribute(embed_sens_t, camera_bp))
                    s_attrib.append(Attribute(embed_sens_t, cameraSem_bp))
                self.agents.append(Agent("vehicle", n_vehicle, out_path, v_attrib, s_attrib))
                n_vehicle=n_vehicle+1
            else:
                print(atype + " is an unknown type")
                out_path = None
            oxts.append({"type": atype, "path": out_path})

        

        if not os.path.exists('%s/' % (self.path)):
            try:
                os.makedirs('%s/' % (self.path))
            except OSError:
                print('Failed creating directory %s' % ('%s/' % (self.path)))

        out_config = {"agents": oxts}
        f = open('%s/information.json' % (self.path), "w")
        JDump = json.dumps(out_config)
        f.write(JDump)
        f.close()

    def spawn_actors(self, world, queue):
        self.actor_list = []
        for agent in self.agents:
            self.actor_list = self.actor_list + agent.spawn(world, queue)
            print(agent.get_actors_list())
        return self.actor_list

    def get_agents(self):
        return self.agents

    def get_nframes(self):
        return self.nframe

                

if __name__ == '__main__':
    config = Config()
    config.read_json("./config/test2.json")
    print(config)