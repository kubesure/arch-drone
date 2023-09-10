import cv2
from djitellopy import Tello
from detector import edge as ed
import config_loader 

class TelloVideoStream:
    def __init__(self, tello):
        self.tello = tello
        self.frame_read = self.tello.get_frame_read()

    def start(self):
        detector = ed.EdgeDector(config_loader.get_configurations())

        while True:
            frame = self.frame_read.frame
            detector.get_x_y_z(frame)
            cv2.imshow("Tello Video Feed", frame)
           
            # Press 'q' to exit the video window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

# Connect to Tello and start video streaming
tello = Tello()
tello.connect()
tello.streamon()

video_stream = TelloVideoStream(tello)
video_stream.start()

tello.streamoff()


