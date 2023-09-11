import cv2
from djitellopy import Tello
from detector import edge as ed
import config_loader 
from time import sleep
import threading

class TelloVideoStream:
    def __init__(self, drone):
        self.drone = drone
        self.frame_read = self.drone.get_frame_read()   

    def start(self):
        detector = ed.EdgeDector(config_loader.get_configurations())

        while True:
            frame = self.frame_read.frame
            result = detector.get_x_y_z(frame)
            if result is not None:
                x,y,z,area = result
                print(f"x: {x}, y: {y}, z: {z} area {area}")
            else:
                pass
                #print("No suitable contour found") 

            cv2.imshow("Drone Video Feed", frame)
           
            # Press 'q' to exit the video window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

def process_video(drone,config):
    video_stream = TelloVideoStream(drone)
    video_stream.start()

def drone_takeoff_n_look(drone,config):
    drone.takeoff()
    drone.move_up(config['red_optimum_hover_ht'])
    hover = True
    time = 1
    while hover:
        detector = ed.EdgeDector(config_loader.get_configurations())
        result = detector.get_x_y_z()
        sleep(1)
        time = time + 1
        if time == 10:
            hover = False
    if result is not None:
        x,y,z = result
        print(f"x: {x}, y: {y}, z: {z}")
        return result
    else:
        return None

def drone_navigate_to_next(drone,coordinates):
    pass

def drone_scan_next(drone):
    pass

if __name__ == '__main__':
    config = config_loader.get_configurations()
    drone = Tello()
    drone.connect()
    drone.streamoff()
    drone.streamon()

    process_video(drone,config)

    #coordinates = drone_takeoff_n_look(drone,config)  
    #drone_navigate_to_next(drone,coordinates)
    #drone_takeoff_n_look(drone,config)
    
    drone.streamoff()
    drone.land()


    
   
    

   


