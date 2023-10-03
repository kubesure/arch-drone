import queue

import plotter
from drone_types import Ring, DroneErrorCode
from collections import Counter
import cv2
from datetime import datetime
from cv2 import VideoWriter
from typing import List
import drone_types


def ring_detected(r: Ring) -> (bool, Ring):
    if r.z == 0 or r.y == 0 or r.y == 0:
        return False, Ring
    return True, r


def filter_zero_distances(rings):
    rings_detected: List[Ring] = []
    for ring in rings:
        if ring_detected(ring):
            rings_detected.append(ring)
    return rings_detected


def get_short_or_longest_distance(rings, longest) -> (bool, Ring):
    print(f"finding short of long ring out of rings {len(rings)}")

    rings = filter_zero_distances(rings)
    print(f"Ring for long short after filter {len(rings)}")

    if len(rings) == 0:
        return False, None
    sorted_rings = sorted(rings, key=lambda ring: ring.z, reverse=longest)
    return True, sorted_rings[0]


def get_avg_distance(rings) -> (bool, Ring):
    print(f"Ring for average {len(rings)}")

    rings = filter_zero_distances(rings)
    print(f"Ring for average after filter {len(rings)}")

    rings_to_consider = get_percentage_rings(rings, .50)
    print(f"total rings {len(rings)} rings considered for avg {len(rings_to_consider)}")

    avg_x = int(sum(ring.x for ring in rings_to_consider) / len(rings_to_consider))
    avg_y = int(sum(ring.y for ring in rings_to_consider) / len(rings_to_consider))
    avg_z = int(sum(ring.z for ring in rings_to_consider) / len(rings_to_consider))
    avg_area = int(sum(ring.area for ring in rings_to_consider) / len(rings_to_consider))
    color_counts = Counter(ring.color for ring in rings_to_consider)
    avg_color = color_counts.most_common(1)[0][0]
    average_ring = Ring(x=avg_x, y=avg_y, z=avg_z, area=avg_area, color=avg_color)
    print(f"Returning the AVG ring {average_ring}")
    return True, average_ring


def get_percentage_rings(rings, percent_to_discard):
    num_to_consider = int(len(rings) * (1 - percent_to_discard))
    rings_to_consider = rings[-num_to_consider:]
    return rings_to_consider


class Cv2CapReader:
    def __init__(self):
        drone_video_url = 'udp://@0.0.0.0:11111'
        self.cap = cv2.VideoCapture(drone_video_url)
        self.cap.set(cv2.CAP_PROP_FPS, drone_types.FPS30)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Couldn't read a frame from video.")
            return None
        return ret, frame


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


def get_out_writer(write_vid):
    video_reader = Cv2CapReader()
    ret, frame = video_reader.get_frame()
    out_writer: VideoWriter
    if ret:
        if write_vid:
            height, width, _ = frame.shape
            out_writer = vid_writer(width, height)
            return out_writer, video_reader
    return None, None


class DroneException(Exception):
    def __init__(self, message="Internal error occurred", code=DroneErrorCode.InternalError):
        self.message = message
        self.error_code = code
        super().__init__(self.message)

    def get_error_message(self):
        return f"code {self.error_code}: message {self.message}"

    def get_error_code(self):
        return self.error_code


def drone_land_sequence(drone):
    drone.land()
    drone.streamoff()
    drone.end()


# write without detect
def record_navigation(done: queue.Queue, write_vid: bool):
    out_writer, video_reader = get_out_writer(write_vid)
    while not done.get():
        ret,  frame = video_reader.get_frame()
        if ret:
            if write_vid:
                out_writer.write(frame)
