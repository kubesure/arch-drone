from djitellopy import Tello
from detector import contour_edge 
import config_loader 
from time import sleep
import plotter
import navigator
from drone_types import RingColor 
  
def process_video(drone,config):
    video_stream = plotter.TelloVideoStream(drone)
    video_stream.start()

def drone_takeoff_n_detect(drone,config):
    drone.move_up(config['red_optimum_hover_ht'])
    hover = True
    time = 20
    drone.streamoff()
    drone.streamon()
    drone.takeoff()
    drone.move_up(150)

    while hover:
        sleep(1)
        time = time + 1
        if time == 20:
            hover = False

    

if __name__ == '__main__':
    config = config_loader.get_configurations()
    drone = Tello()
    drone.connect() 
   
    ring_sequence =  [RingColor.RED,RingColor.YELLOW,RingColor.RED,RingColor.YELLOW],  
    rings = drone_takeoff_n_detect(drone,ring_sequence)
    while True:
        navigator.navigate(drone,rings)

    


    
   
    

   


