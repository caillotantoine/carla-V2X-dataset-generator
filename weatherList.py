import glob
import os
import sys

# Import de CARLA depuis le egg
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random

weather_clear_dusk = carla.WeatherParameters(cloudiness=0.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=-5.0, sun_azimuth_angle=0.0)
weather_clear_sunrise = carla.WeatherParameters(cloudiness=0.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=10.0, sun_azimuth_angle=10.0)
weather_clear_30deg = carla.WeatherParameters(cloudiness=0.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=30.0, sun_azimuth_angle=30.0)
weather_clear_60deg = carla.WeatherParameters(cloudiness=0.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=60.0, sun_azimuth_angle=120.0)
weather_clear_noon = carla.WeatherParameters(cloudiness=0.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=80.0, sun_azimuth_angle=90.0)
weather_clear_night = carla.WeatherParameters(cloudiness=0.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=-90.0, sun_azimuth_angle=0.0)

weather_lightCloud_dusk = carla.WeatherParameters(cloudiness=30.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=-5.0, sun_azimuth_angle=0.0)
weather_lightCloud_sunrise = carla.WeatherParameters(cloudiness=30.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=10.0, sun_azimuth_angle=10.0)
weather_lightCloud_30deg = carla.WeatherParameters(cloudiness=30.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=30.0, sun_azimuth_angle=30.0)
weather_lightCloud_60deg = carla.WeatherParameters(cloudiness=30.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=60.0, sun_azimuth_angle=120.0)
weather_lightCloud_noon = carla.WeatherParameters(cloudiness=30.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=80.0, sun_azimuth_angle=90.0)
weather_lightCloud_night = carla.WeatherParameters(cloudiness=30.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=-90.0, sun_azimuth_angle=0.0)

weather_cloudy_dusk = carla.WeatherParameters(cloudiness=70.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=-5.0, sun_azimuth_angle=0.0)
weather_cloudy_sunrise = carla.WeatherParameters(cloudiness=70.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=10.0, sun_azimuth_angle=10.0)
weather_cloudy_30deg = carla.WeatherParameters(cloudiness=70.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=30.0, sun_azimuth_angle=30.0)
weather_cloudy_60deg = carla.WeatherParameters(cloudiness=70.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=60.0, sun_azimuth_angle=120.0)
weather_cloudy_noon = carla.WeatherParameters(cloudiness=70.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=80.0, sun_azimuth_angle=90.0)
weather_cloudy_night = carla.WeatherParameters(cloudiness=70.0, precipitation=0.0, precipitation_deposits=0.0, sun_altitude_angle=-90.0, sun_azimuth_angle=0.0)

weather_lightRain_dusk = carla.WeatherParameters(cloudiness=100.0, precipitation=30.0, precipitation_deposits=30.0, sun_altitude_angle=-5.0, sun_azimuth_angle=0.0)
weather_lightRain_sunrise = carla.WeatherParameters(cloudiness=100.0, precipitation=30.0, precipitation_deposits=30.0, sun_altitude_angle=10.0, sun_azimuth_angle=10.0)
weather_lightRain_30deg = carla.WeatherParameters(cloudiness=100.0, precipitation=30.0, precipitation_deposits=30.0, sun_altitude_angle=30.0, sun_azimuth_angle=30.0)
weather_lightRain_60deg = carla.WeatherParameters(cloudiness=100.0, precipitation=30.0, precipitation_deposits=30.0, sun_altitude_angle=60.0, sun_azimuth_angle=120.0)
weather_lightRain_noon = carla.WeatherParameters(cloudiness=100.0, precipitation=30.0, precipitation_deposits=30.0, sun_altitude_angle=80.0, sun_azimuth_angle=90.0)
weather_lightRain_night = carla.WeatherParameters(cloudiness=100.0, precipitation=30.0, precipitation_deposits=30.0, sun_altitude_angle=-90.0, sun_azimuth_angle=0.0)

weather_rain_dusk = carla.WeatherParameters(cloudiness=100.0, precipitation=70.0, precipitation_deposits=70.0, sun_altitude_angle=-5.0, sun_azimuth_angle=0.0)
weather_rain_sunrise = carla.WeatherParameters(cloudiness=100.0, precipitation=70.0, precipitation_deposits=70.0, sun_altitude_angle=10.0, sun_azimuth_angle=10.0)
weather_rain_30deg = carla.WeatherParameters(cloudiness=100.0, precipitation=70.0, precipitation_deposits=70.0, sun_altitude_angle=30.0, sun_azimuth_angle=30.0)
weather_rain_60deg = carla.WeatherParameters(cloudiness=100.0, precipitation=70.0, precipitation_deposits=70.0, sun_altitude_angle=60.0, sun_azimuth_angle=120.0)
weather_rain_noon = carla.WeatherParameters(cloudiness=100.0, precipitation=70.0, precipitation_deposits=70.0, sun_altitude_angle=80.0, sun_azimuth_angle=90.0)
weather_rain_night = carla.WeatherParameters(cloudiness=100.0, precipitation=70.0, precipitation_deposits=70.0, sun_altitude_angle=-90.0, sun_azimuth_angle=0.0)

weather_fog_dusk = carla.WeatherParameters(cloudiness=100.0, precipitation=10.0, precipitation_deposits=10.0, fog_density=50.0, fog_distance=0.0, fog_falloff=0.10, sun_altitude_angle=-5.0, sun_azimuth_angle=0.0)
weather_fog_sunrise = carla.WeatherParameters(cloudiness=100.0, precipitation=10.0, precipitation_deposits=10.0, fog_density=50.0, fog_distance=0.0, fog_falloff=0.10, sun_altitude_angle=10.0, sun_azimuth_angle=10.0)
weather_fog_30deg = carla.WeatherParameters(cloudiness=100.0, precipitation=10.0, precipitation_deposits=10.0, fog_density=50.0, fog_distance=0.0, fog_falloff=0.10, sun_altitude_angle=30.0, sun_azimuth_angle=30.0)
weather_fog_60deg = carla.WeatherParameters(cloudiness=100.0, precipitation=10.0, precipitation_deposits=10.0, fog_density=50.0, fog_distance=0.0, fog_falloff=0.10, sun_altitude_angle=60.0, sun_azimuth_angle=120.0)
weather_fog_noon = carla.WeatherParameters(cloudiness=100.0, precipitation=10.0, precipitation_deposits=10.0, fog_density=50.0, fog_distance=0.0, fog_falloff=0.10, sun_altitude_angle=80.0, sun_azimuth_angle=90.0)
weather_fog_night = carla.WeatherParameters(cloudiness=100.0, precipitation=10.0, precipitation_deposits=10.0, fog_density=50.0, fog_distance=0.0, fog_falloff=0.10, sun_altitude_angle=-90.0, sun_azimuth_angle=0.0)
