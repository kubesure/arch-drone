import cv2
from datetime import datetime
from cv2 import VideoWriter
from typing import List
from drone_types import Ring,RingColor
from detector import contour_edge
import time
from djitellopy import Tello


class Cv2CapReader:
    def __init__(self):
        drone_video_url = 'udp://@0.0.0.0:11111'
        self.cap = cv2.VideoCapture(drone_video_url)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Couldn't read a frame from video.")
            return None
        return frame


class DJIFrameRead:
    def __init__(self, drone):
        self.frame_read = drone.get_frame_read()

    def get_frame(self):
        ret, frame = self.frame_read.frame
        if not ret:
            print("Error: Couldn't read a frame from video.")
            return None
        return frame


def vid_writer(width, height):
    current_time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video_path = f"./data/videos/test_run_{current_time_str}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (width, height))
    return out_writer


def plot(write_vid, detect: bool, duration, ring, drone: Tello):
    rings_detected: List[Ring] = []
    drone.streamoff()
    drone.streamon()

    video_reader = Cv2CapReader()
    frame = video_reader.get_frame()

    out_writer: VideoWriter
    if write_vid:
        height, width, _ = frame.shape
        out_writer = vid_writer(width, height)

    start_time = time.time()
    while int(time.time() - start_time) < duration:
        frame = video_reader.get_frame()

        if detect:
            r, detected_frame = contour_edge.get_xyz_area(frame, ring)
            frame = detected_frame
            rings_detected.append(r)
        if write_vid:
            out_writer.write(frame)

    if write_vid:
        out_writer.release()
    drone.streamoff()
    return rings_detected


def mock_plot(write_vid, detect: bool, duration, ring):
    rings_detected: List[Ring] = [Ring(x=34, y=45, z=150, area=0, color=ring)]
    return rings_detected
