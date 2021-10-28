import carla
from carla import Transform
from carla import VehicleLightState as vls
from typing import List

class Attribute:
    def __init__(self, pose: Transform, bp, save_path: str):
        self.pose = pose
        self.bp = bp
        self.save_path = save_path
        self.actor_id = None
        self.actor = None
        if self.bp.id.find('vehicle') != -1:
            self.type = 'v'
        elif self.bp.id.find('sensor') != -1:
            self.type = 's'
        else:
            self.type = 'u'

    def save(self, data: any, frame:int, color_converter=None):
        if self.type == 's':
            if color_converter == None:
                data.save_to_disk(self.save_path%frame)
            else:
                data.save_to_disk(self.save_path%frame, color_converter)

    def set_actor_id(self, actor_id):
        self.actor_id = actor_id

    def get_actor_id(self):
        return self.actor_id

    def get_actor(self):
        return self.actor

    def spawn(self, world:carla.World, autopilot=None, attach_to=None) -> None:
        try:
            actor = world.spawn_actor(self.bp, self.pose, attach_to=attach_to)
            if autopilot != None:
                actor.set_autopilot(autopilot)
            self.actor = actor
            self.actor_id = actor.id
        except Exception as e:
            print("Exception spawning actor : {}".format(e))
        
        
class Agent:
    def __init__(self, type: str, agentN, vehicle=None, sensors=None):
        self.type = type
        self.agentN = agentN
        self.vehicle:Attribute = vehicle
        self.sensors:List[Attribute] = sensors

    def get_vehicle(self) -> Attribute:
        return self.vehicle

    def get_sensors(self) -> List[Attribute]:
        return self.sensors

    def spawn(self, world) -> List[int]:
        parent=None
        actors_id:List[int] = []
        if self.vehicle != None:
            self.vehicle.spawn(world, autopilot=True)
            parent = self.vehicle.get_actor()
            actors_id.append(self.vehicle.get_actor_id())
        for sensor in self.sensors:                                 # Bug potentiel. Est-ce une référence? Une copie de la variable? 
            sensor.spawn(world, attach_to=parent)                   # Si bug -> fix avec un enumerate
            # TODO listener pout placer dans une queue
            actors_id.append(sensor.get_actor_id())
        return actors_id

    def get_actors_list(self) -> List[int]:
        out:List[int] = []
        if self.vehicle.get_actor_id() != None:
            out.append(self.vehicle.get_actor_id())
        for sensor in self.sensors:
            if sensor.get_actor_id() != None:
                out.append(sensor.get_actor_id())
        return out



if __name__ == '__main__':
    test = Agent("None", 0)
    v = test.get_vehicle()
    print(v)
