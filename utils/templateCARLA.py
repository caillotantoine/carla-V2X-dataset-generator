import carla

def main():

    print('This script does not check the version compatibility between carla and the script. It was developed under the 0.9.11 version. Errors might be expected if ran from another version.')

    client = carla.Client('localhost', 2000)    # Parameters of the CARLA server
    client.set_timeout(10.0)                    # Timeout to connect to the server

    print('You are connected to the simulator.')

    try: 
        # Infinite loop to wait the end of the world
        # print('Press Ctrl+C to quit')
        # while True:
        #     world.wait_for_tick()
        pass

    finally:
        # print('Destroying actors')
        # client.apply_batch([carla.command.DestroyActor(x) for x in vehicle_list])
        # print('Actors destroyed')
        pass
    
if __name__ == '__main__':
    main()
