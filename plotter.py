import cv2
from datetime import datetime
from cv2 import VideoWriter
from typing import List
from drone_types import Ring,RingColor
from detector import contour_edge
import time


def vid_writer(width, height):
    current_time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video_path = f"./data/videos/test_run_{current_time_str}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (width, height))
    return out_writer


def plot(write_vid, detect: bool, duration, ring):
    drone_video_url = 'udp://@0.0.0.0:11111'
    cap = cv2.VideoCapture(drone_video_url)

    rings_detected: List[Ring] = []

    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't read a frame from video.")
        return
    height, width, _ = frame.shape
    out_writer: VideoWriter

    if write_vid:
        out_writer = vid_writer(width, height)
    start_time = time.time()

    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()

        if not ret:
            break
        if detect:
            r = contour_edge.get_xyz_area(frame, ring)
            rings_detected.append(r)
        if write_vid:
            out_writer.write(frame)

    cap.release()
    if write_vid:
        out_writer.release()
    return rings_detected


def mock_plot(write_vid, detect: bool, duration, ring):
    rings_detected: List[Ring] = [Ring(x=34, y=45, z=150, area=0, color=ring)]
    return rings_detected

if __name__ == '__main__':
    plot(True, True, 10, RingColor.RED)
