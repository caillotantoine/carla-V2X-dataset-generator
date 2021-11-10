import glob
import os
import sys
import numpy as np
from math import pi, tan

import carla
from utils.sensors import *
import json


# from sensors import *

def saveImageRGBAndT(world, image, sensor, path, parent=None):
    image.save_to_disk('%s/cameraRGB/%06d.png' % (path, image.frame))
    Tsensor = sensor.get_transform().get_matrix()
    Lsensor = world.get_map().transform_to_geolocation(sensor.get_location())
    if(parent == None):
        if not os.path.exists(path):
            try: 
                os.makedirs(path)
            except OSError:
                print("Error creating %s" % path)
                sys.exit()
        else:
            if not os.path.exists('%s/sensor.json' % path):
                f = open('%s/sensor.json' % path, "w")
                JDump = json.dumps({"sensor":{"T_Mat" : Tsensor, "loc": {"lat": Lsensor.latitude, "lon": Lsensor.longitude, "alt": Lsensor.altitude}}})
                f.write(JDump)
                f.close()
    else:
        Tv = parent.get_transform().get_matrix()
        Lv = world.get_map().transform_to_geolocation(parent.get_location())
        Vv = parent.get_velocity()
        AVv = parent.get_angular_velocity()
        Av = parent.get_acceleration()
        FVv = parent.get_transform().get_forward_vector()
        BBox = parent.bounding_box
        if not os.path.exists('%s/VehicleInfo' % path):
            try: 
                os.makedirs('%s/VehicleInfo' % path)
            except OSError:
                print("Error creating %s/VehicleInfo" % path)
                sys.exit()
        else:
            f = open('%s/VehicleInfo/%06d.json' % (path, image.frame), "w")
            JDump = json.dumps({"sensor":{"T_Mat" : Tsensor, "loc": {"lat": Lsensor.latitude, "lon": Lsensor.longitude, "alt": Lsensor.altitude}}, "vehicle": {"T_Mat": Tv, "loc": {"lat": Lv.latitude, "lon": Lv.longitude, "alt": Lv.altitude}, "velocity": {"x": Vv.x,"y": Vv.y, "z": Vv.z}, "ang_velocity": {"x": AVv.x,"y": AVv.y, "z": AVv.z}, "accel": {"x": Av.x,"y": Av.y, "z": Av.z}, "forward_vector": {"x": FVv.x,"y": FVv.y, "z": FVv.z}, "BoundingBox": {"extent": {"x": BBox.extent.x,"y": BBox.extent.y, "z": BBox.extent.z}, "loc": {"x": BBox.location.x,"y": BBox.location.y, "z": BBox.location.z}, "rot": {"pitch": BBox.rotation.pitch,"yaw": BBox.rotation.yaw, "roll": BBox.rotation.roll}}}})
            f.write(JDump)
            f.close()
        # try: 
        #     os.makedirs('%s/')
        # f = open("%s/sensor")



def writeCameraMatrix(camera_bp, path):
    cameraFOV = camera_bp.get_attribute('fov').as_float()
    cameraFocal = camera_bp.get_attribute('focal_distance').as_float()
    # print(cameraFocal)
    img_w = camera_bp.get_attribute('image_size_x').as_int()
    img_h = camera_bp.get_attribute('image_size_y').as_int()
    focal = img_w / (2 * tan(cameraFOV * pi / 360))
    c_u = img_w / 2.0
    c_v = img_h / 2.0
    k = np.zeros((3,3), dtype=float)
    k[0,0] = focal 
    k[1,1] = focal
    k[2,2] = 1.0
    k[0,2] = c_u
    k[1,2] = c_v
    # print('Camera Matrix:')
    # print(k)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            print('Failed creating directory %s' % path)
    if not os.path.exists('%s/cameraMatrix.npy'%path):
        np.save('%s/cameraMatrix.npy'%path, k)


    

def spawnSensors(world, actor_list, path, transform, parent=None):
    blueprint_library = world.get_blueprint_library()

    camera_bp = get_KITTIcam_bp(blueprint_library)
    cameraDepth_bp = get_KITTIcamDepth_bp(blueprint_library)
    cameraSem_bp = get_KITTIcamSem_bp(blueprint_library)
    VLP32_bp = get_VLP32_bp(blueprint_library)
    # GNSS_bp = get_GNSS(blueprint_library)
    # IMU_bp = get_IMU(blueprint_library)

    camRGB = None 
    camSem = None
    camDepth = None
    LiDAR = None
    
    
    if(parent == None):
        camRGB  = world.try_spawn_actor(camera_bp, transform)
        camDepth  = world.try_spawn_actor(cameraDepth_bp, transform)
        camSem  = world.try_spawn_actor(cameraSem_bp, transform)
        LiDAR = world.try_spawn_actor(VLP32_bp, carla.Transform(transform.location))
        # GNSS = world.try_spawn_actor(GNSS_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        # IMU = world.try_spawn_actor(IMU_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
    else:
        camRGB  = world.try_spawn_actor(camera_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        camDepth  = world.try_spawn_actor(cameraDepth_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        camSem  = world.try_spawn_actor(cameraSem_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        LiDAR = world.try_spawn_actor(VLP32_bp, carla.Transform(transform.location), attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        # GNSS = world.try_spawn_actor(GNSS_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        # IMU = world.try_spawn_actor(IMU_bp, transform, attach_to=parent, attachment_type=carla.AttachmentType.Rigid)
        pass

    if camRGB == None:
        print('Failed to spawn the camera RGB')
    else:
        # print(camRGB.get_transform().get_matrix())
        camRGB.listen(lambda image: saveImageRGBAndT(world, image, camRGB, path, parent))
        writeCameraMatrix(camera_bp, '%s/cameraRGB'%path)
        actor_list.append(camRGB.id)

    if camDepth == None:
        print('Failed to spawn the camera Depth')
    else:
        camDepth.listen(lambda image: image.save_to_disk('%s/cameraDepth/%06d.png' % (path, image.frame), carla.ColorConverter.LogarithmicDepth))
        actor_list.append(camDepth.id)

    if camSem == None:
        print('Failed to spawn the camera Sem')
    else:
        camSem.listen(lambda image: image.save_to_disk('%s/cameraSem/%06d.png' % (path, image.frame), carla.ColorConverter.CityScapesPalette))
        actor_list.append(camSem.id)

    if LiDAR == None:
        print('Failed to spawn the LiDAR')
    else:
        LiDAR.listen(lambda pointcloud: pointcloud.save_to_disk('%s/LiDAR/%06d.ply' % (path, pointcloud.frame)))
        actor_list.append(LiDAR.id)

    # if GNSS == None:
    #     print('Failed to spawn the camera RGB')
    # else:
    #     if(parent == None):
    #         GNSS.listen(lambda gnssMeasurement: writeGNSS(gnssMeasurement, path))
    #     else: # Only register several frames when attached to a parent
    #         GNSS.listen(lambda gnssMeasurement: writeGNSS(gnssMeasurement, path))
    #     actor_list.append(GNSS.id)
    

    return (camRGB, camDepth, camSem, LiDAR)

