from detector import contour_edge
from drone_types import RingColor 
import cv2

def plot(drone,sequence):
    
    #output_video_path = "./data/videos/test_run_1209.mov"
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #out_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (1280, 720))
    frame_read = drone.get_frame_read()   

    while True:
        frame = frame_read.frame
        rings = contour_edge.get_xyz_rings(sequence)
        cv2.imshow("Drone Video Feed", frame)
        
        # Press 'q' to exit the video window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cv2.destroyAllWindows()