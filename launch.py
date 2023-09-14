from djitellopy import Tello
import config_loader 
from time import sleep
import plotter
#import navigator
from drone_types import RingColor 
  
def process_video(drone,ring_sequence):
    drone.streamoff()
    drone.streamon()
    #drone.takeoff()
    #drone.move_up(150)
    plotter.plot(drone,ring_sequence)

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
   
    ring_sequence =  [RingColor.RED,RingColor.YELLOW]
    process_video(drone,ring_sequence)

    '''  
    rings = drone_takeoff_n_detect(drone,ring_sequence)
    if len(rings) > 1:
        task_done = False
        while not task_done:
            task_done = navigator.navigate(drone,rings)
    '''        

    


    
   
    

   


