import glob
import os
import sys

# Import CARLA from the egg
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def get_VLP16_bp (blueprint_library):
    VLP16_bp = blueprint_library.find('sensor.lidar.ray_cast')

    VLP16_bp.set_attribute('rotation_frequency','20')
    VLP16_bp.set_attribute('channels','16')
    VLP16_bp.set_attribute('points_per_second','300000')
    VLP16_bp.set_attribute('range','100.0')
    VLP16_bp.set_attribute('upper_fov','15.0')
    VLP16_bp.set_attribute('lower_fov','-15.0')
    return VLP16_bp

def get_VLP32_bp (blueprint_library):
    VLP32_bp = blueprint_library.find('sensor.lidar.ray_cast')

    VLP32_bp.set_attribute('rotation_frequency','20')
    VLP32_bp.set_attribute('channels','32')
    VLP32_bp.set_attribute('points_per_second','1200000')
    VLP32_bp.set_attribute('range','200.0')
    VLP32_bp.set_attribute('upper_fov','15.0')
    VLP32_bp.set_attribute('lower_fov','-25.0')
    return VLP32_bp

def get_HDL64_bp (blueprint_library):
    HDL64_bp = blueprint_library.find('sensor.lidar.ray_cast')

    HDL64_bp.set_attribute('rotation_frequency','20')
    HDL64_bp.set_attribute('channels','64')
    HDL64_bp.set_attribute('points_per_second','2200000')
    HDL64_bp.set_attribute('range','120.0')
    HDL64_bp.set_attribute('upper_fov','2.0')
    HDL64_bp.set_attribute('lower_fov','-24.8')
    return HDL64_bp

def get_camera_bp(blueprint_library, w=640, h=480, fov=110):
    camera = blueprint_library.find('sensor.camera.rgb')
    camera.set_attribute('image_size_x', '%d'%w)
    camera.set_attribute('image_size_y', '%d'%h)
    camera.set_attribute('fov', '%d'%fov)
    return camera

def get_KITTIcam_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.rgb')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '90') 
    return camera

def get_KITTIcamWide_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.rgb')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '125') 
    return camera

def get_KITTIcamOmni_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.rgb')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '170') 
    return camera

def get_KOPERcam_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.rgb')
    camera.set_attribute('image_size_x', '656')
    camera.set_attribute('image_size_y', '494')
    camera.set_attribute('fov', '75')
    return camera

def get_KOPERcamWide_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.rgb')
    camera.set_attribute('image_size_x', '656')
    camera.set_attribute('image_size_y', '494')
    camera.set_attribute('fov', '125')
    return camera



## Depth

def get_cameraDepth_bp(blueprint_library, w=640, h=480, fov=110):
    camera = blueprint_library.find('sensor.camera.depth')
    camera.set_attribute('image_size_x', '%d'%w)
    camera.set_attribute('image_size_y', '%d'%h)
    camera.set_attribute('fov', '%d'%fov)
    return camera

def get_KITTIcamDepth_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.depth')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '90') 
    return camera

def get_KITTIcamWideDepth_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.depth')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '125') 
    return camera

def get_KITTIcamOmniDepth_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.depth')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '170') 
    return camera

def get_KOPERcamDepth_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.depth')
    camera.set_attribute('image_size_x', '656')
    camera.set_attribute('image_size_y', '494')
    camera.set_attribute('fov', '75')
    return camera

def get_KOPERcamWideDepth_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.depth')
    camera.set_attribute('image_size_x', '656')
    camera.set_attribute('image_size_y', '494')
    camera.set_attribute('fov', '125')
    return camera


## segm

def get_cameraSem_bp(blueprint_library, w=640, h=480, fov=110):
    camera = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera.set_attribute('image_size_x', '%d'%w)
    camera.set_attribute('image_size_y', '%d'%h)
    camera.set_attribute('fov', '%d'%fov)
    return camera

def get_KITTIcamSem_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '90') 
    return camera

def get_KITTIcamWideSem_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '125') 
    return camera

def get_KITTIcamOmniSem_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera.set_attribute('image_size_x', '1384')
    camera.set_attribute('image_size_y', '1032')
    camera.set_attribute('fov', '170') 
    return camera

def get_KOPERcamSem_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera.set_attribute('image_size_x', '656')
    camera.set_attribute('image_size_y', '494')
    camera.set_attribute('fov', '75')
    return camera

def get_KOPERcamWideSem_bp(blueprint_library):
    camera = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera.set_attribute('image_size_x', '656')
    camera.set_attribute('image_size_y', '494')
    camera.set_attribute('fov', '125')
    return camera

# Other sensors
def get_GNSS(blueprint_library):
    gnss = blueprint_library.find('sensor.other.gnss')
    return gnss

def get_IMU(blueprint_library):
    imu = blueprint_library.find('sensor.other.imu')
    return imu