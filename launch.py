import cv2
from djitellopy import Tello
from detector import edge as ed
import config_loader 
from time import sleep
  

class TelloVideoStream:
    def __init__(self, drone):
        self.drone = drone
        self.frame_read = self.drone.get_frame_read()   

    def start(self):
        detector = ed.EdgeDector(config_loader.get_configurations())
        #output_video_path = "./data/videos/test_run_1209.mov"
        #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        #out_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (1280, 720))

        while True:
            frame = self.frame_read.frame
            result = detector.get_x_y_z(frame)
            #out_writer(frame)
            if result is not None:
                x,y,z,area = result
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
    time = 20
    detector = ed.EdgeDector(config_loader.get_configurations())

    x_cm, y_cm, z_cm = 0  
    result_all = (0,0,0)

    while hover:
        result_all = detector.get_x_y_z()
        sleep(1)
        time = time + 1
        if time == 20:
            hover = False

    if result_all is not None:
        x,y,z = result_all
        x_cm = x 
        y_cm = y
        z_cm = z
        print(f"x: {x_cm}, y: {y_cm}, z: {z_cm}")
        return result_all
    else:
        return None

def drone_navigate_to_next(drone):
    drone.move_up(200)
    drone.move_forward(500)

def drone_scan_next(drone):
    pass

if __name__ == '__main__':
    config = config_loader.get_configurations()
    drone = Tello()
    drone.connect()
    
    drone.streamoff()
    drone.streamon()
    drone.takeoff()
    #drone.move_up(150)
    #process_video(drone,config)

    #coordinates = drone_takeoff_n_look(drone,config)  
    drone_navigate_to_next(drone)
    #drone_takeoff_n_look(drone,config)
   
    
    drone.streamoff()
    drone.land()


    
   
    

   


