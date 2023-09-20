from detector import contour_edge
import cv2
from datetime import datetime
from cv2 import VideoWriter


def vid_writer(width, height):
    current_time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video_path = f"./data/videos/test_run_{current_time_str}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (width, height))
    return out_writer


def plot(write_vid, detect: bool):
    drone_video_url = 'udp://@0.0.0.0:11111'
    cap = cv2.VideoCapture(drone_video_url)
    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't read a frame from video.")
        return
    height, width, _ = frame.shape
    # out_writer: VideoWriter

    if write_vid:
        out_writer = vid_writer(width, height)
        pass

    while True:
        ret, frame = cap.read()

        if not ret:
            break
        if detect:
            pass
        if write_vid:
            # out_writer.write(frame)
            pass

        cv2.imshow("Drone detection feed", frame)
        
        # Press 'q' to exit the video window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()    
    # out_writer.release()
    cv2.destroyAllWindows()
