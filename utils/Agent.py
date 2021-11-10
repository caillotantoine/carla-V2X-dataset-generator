import carla
from carla import Transform
from carla import VehicleLightState as vls
from typing import List
import queue
import numpy as np
from math import pi, tan
import json
import os

class Attribute:
    def __init__(self, pose: Transform, bp, save_path: str = None, color_converter=carla.ColorConverter.Raw, maxspeed:float=0.0):
        self.pose = pose
        self.bp = bp
        self.actor_id = None
        self.actor = None
        self.color_conv = color_converter
        self.types = self.bp.id.split('.')
        self.maxspeed = maxspeed
        self.save_path = save_path
        if self.save_path != None:
            if self.types[0] == 'sensor':
                self.save_path = self.save_path + self.types[1] + '_' + self.types[2] + '/'
            if self.types[0] == 'vehicle':
                self.save_path = self.save_path + "infos/"
    
    def set_save_path(self, save_path: str):
        self.save_path = save_path
        if self.save_path != None:
            if self.types[0] == 'sensor':
                self.save_path = self.save_path + self.types[1] + '_' + self.types[2] + '/'
            if self.types[0] == 'vehicle':
                self.save_path = self.save_path + "infos/"

    def spawn(self, world:carla.World, autopilot=None, attach_to=None, to_save:queue.Queue=None) -> None:
        if self.types[0] == 'controller':
            world.tick()
        try:
            actor = world.spawn_actor(self.bp, self.pose, attach_to=attach_to)
            if self.types[0] == 'vehicle':
                if autopilot != None:
                    actor.set_autopilot(autopilot)
            if self.types[0] != 'controller' and to_save != None:
                actor.listen(lambda data: to_save.put((self, data)))
            if self.types[0] == 'controller':
                actor.start()
                actor.go_to_location(world.get_random_location_from_navigation())
                # actor.set_max_speed(self.maxspeed)
            self.actor = actor
            if self.types[0] != 'controller':
                self.actor_id = actor.id
            else:
                self.actor_id = None
        except Exception as e:
            print("Exception spawning actor : {}".format(e))

    def get_camera_matrix(self):
        cameraFOV = self.bp.get_attribute('fov').as_float()
        img_w = self.bp.get_attribute('image_size_x').as_int()
        img_h = self.bp.get_attribute('image_size_y').as_int()
        focal = img_w / (2 * tan(cameraFOV * pi / 360))
        c_u = img_w / 2.0
        c_v = img_h / 2.0
        k = np.zeros((3,3), dtype=float)
        k[0,0] = focal 
        k[1,1] = focal
        k[2,2] = 1.0
        k[0,2] = c_u
        k[1,2] = c_v
        return k

    def save(self, data: any, frame:int):
        if self.types[1] == "camera":
            data.save_to_disk(self.save_path+'%06d.png'%frame, color_converter=self.color_conv)
            k = self.get_camera_matrix()
            if not os.path.exists(self.save_path):
                try:
                    os.makedirs(self.save_path)
                except OSError:
                    print('Failed creating directory %s' % self.save_path)
            if not os.path.exists('%s/cameraMatrix.npy'%self.save_path):
                np.save('%s/cameraMatrix.npy'%self.save_path, k)

    def set_actor_id(self, actor_id):
        self.actor_id = actor_id

    def get_actor_id(self):
        return self.actor_id

    def get_actor(self):
        return self.actor

    def get_transform(self):
        if self.types[0] != 'walker':
            return self.actor.get_transform().get_matrix()
        return None

    def get_geoloc(self, world):
        return world.get_map().transform_to_geolocation(self.actor.get_location())

    def get_boundingbox(self):
        return self.actor.bounding_box
    
        
class Agent:
    def __init__(self, type: str, agentN, path: str, vehicle=None, sensors=None):
        self.type = type
        self.agentN = agentN
        self.vehicle:Attribute = vehicle
        self.sensors:List[Attribute] = sensors
        self.path = path

        if self.vehicle != None:
            self.vehicle.set_save_path(self.path)
        for s in self.sensors:
            s.set_save_path(save_path=self.path)

    def get_vehicle(self) -> Attribute:
        return self.vehicle

    def get_sensors(self) -> List[Attribute]:
        return self.sensors

    def spawn(self, world, saving_queue:queue.Queue=None) -> List[int]:
        parent=None
        actors_id:List[int] = []
        if self.vehicle != None:
            self.vehicle.spawn(world, autopilot=True)
            parent = self.vehicle.get_actor()
            actors_id.append(self.vehicle.get_actor_id())
        if self.sensors != None:
            for sensor in self.sensors:                                             # Bug potentiel. Est-ce une référence? Une copie de la variable? 
                sensor.spawn(world, attach_to=parent, to_save=saving_queue)         # Si bug -> fix avec un enumerate
                actors_id.append(sensor.get_actor_id())
        return actors_id

    def get_actors_list(self) -> List[int]:
        out:List[int] = []
        if self.vehicle != None:
            if self.vehicle.get_actor_id() != None:
                out.append(self.vehicle.get_actor_id())
        if self.sensors != None:
            for sensor in self.sensors:
                if sensor.get_actor_id() != None:
                    out.append(sensor.get_actor_id())
        return out

    def save_status(self, world, frame):
        vehicle = None
        if self.vehicle != None:
            Tv = self.vehicle.get_transform()
            Lv = self.vehicle.get_geoloc(world)
            BBox = self.vehicle.get_boundingbox()
            vehicle = {"T_Mat": Tv, "loc": {"lat": Lv.latitude, "lon": Lv.longitude, "alt": Lv.altitude}, "BoundingBox": {"extent": {"x": BBox.extent.x,"y": BBox.extent.y, "z": BBox.extent.z}, "loc": {"x": BBox.location.x,"y": BBox.location.y, "z": BBox.location.z}, "rot": {"pitch": BBox.rotation.pitch,"yaw": BBox.rotation.yaw, "roll": BBox.rotation.roll}}}
        
        sensors = []
        if self.sensors != None:
            for n, s in enumerate(self.sensors):
                T = s.get_transform()
                sensors.append({'idx': n, "T_Mat": T})

        if vehicle != None:
            out = {"vehicle": vehicle, "sensors": sensors}
        else:
            out = {"sensors": sensors}
        
        if not os.path.exists('%s/infos/'%self.path):
            try:
                os.makedirs('%s/infos/'%self.path)
            except OSError:
                print('Failed creating directory %s' % ('%s/infos/'%self.path))

        f = open('%s/infos/%06d.json' % (self.path, frame), "w")
        JDump = json.dumps(out)
        f.write(JDump)
        f.close()

if __name__ == '__main__':
    pass
