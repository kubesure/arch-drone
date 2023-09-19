from djitellopy import Tello
import config_loader
import plotter
from navigator import simple
from drone_types import RingColor, Direction


def process_video(drone,ring_sequence):
    drone.streamoff()
    drone.streamon()
    plotter.plot(drone,ring_sequence)


# TODO add exception handling
if __name__ == '__main__':
    ring_sequence = [RingColor.YELLOW, RingColor.RED]
    config = config_loader.get_configurations()
    drone = Tello()
    drone.connect()
    drone.streamoff()
    drone.streamon()
    drone.takeoff()
    navigator = simple.SimpleDroneNavigator(config)
    tasks_done = False
    while not tasks_done:
        for ring in ring_sequence:
            ring_data = navigator.hover_at(ring, Direction.UP)
            navigator.navigate_to(ring_data)
        tasks_done = True
    drone.land()






    
   
    

   


