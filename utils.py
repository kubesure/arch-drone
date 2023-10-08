import numpy as np
from drone_types import Ring, DroneErrorCode
from collections import Counter
import cv2
from datetime import datetime
from cv2 import VideoWriter
from typing import List
import drone_types
import constants
from arch_logger import logger


def ring_detected(r: Ring) -> (bool, Ring):
    if r.z == 0 or r.y == 0 or r.y == 0:
        return False, Ring
    return True, r


def filter_zero_distances(rings):
    rings_detected: List[Ring] = []
    for ring in rings:
        if ring_detected(ring)[0]:
            rings_detected.append(ring)
    return rings_detected


def filter_distance(rings, distance):
    rings_dist_filter: List[Ring] = []
    for ring in rings:
        if ring.z < distance:
            rings_dist_filter.append(ring)
    return rings_dist_filter


def get_short_or_longest_distance(rings, longest) -> (bool, Ring):
    logger.debug(f"finding short of long ring out of rings {len(rings)}")

    rings = filter_zero_distances(rings)
    logger.debug(f"Ring for long short after filter {len(rings)}")

    rings = filter_distance(rings, constants.max_distance_btw_rings)
    logger.debug(f"rings for percentage {rings}")

    if len(rings) == 0:
        return False, None
    sorted_rings = sorted(rings, key=lambda ring: ring.z, reverse=longest)
    return True, sorted_rings[0]


def get_avg_distance(rings) -> (bool, Ring):
    # logger.info(f"Ring for average {len(rings)}")

    rings = filter_zero_distances(rings)
    # logger.info(f"Ring for average after zero filter {len(rings)}")

    max_distance_btw_rings = constants.max_distance_btw_rings
    logger.debug(f"max_distance_btw_rings in get avg distance {max_distance_btw_rings}")
    rings = filter_distance(rings, max_distance_btw_rings)
    logger.debug(f"rings for percentage {rings}")

    rings_to_consider = get_percentage_rings(rings, .50, True)
    logger.debug(f"total rings {len(rings)} rings considered for avg {len(rings_to_consider)}")
    if len(rings_to_consider) > 2:
        avg_x = int(sum(ring.x for ring in rings_to_consider) / len(rings_to_consider))
        avg_y = int(sum(ring.y for ring in rings_to_consider) / len(rings_to_consider))
        avg_z = int(sum(ring.z for ring in rings_to_consider) / len(rings_to_consider))
        avg_area = int(sum(ring.area for ring in rings_to_consider) / len(rings_to_consider))
        color_counts = Counter(ring.color for ring in rings_to_consider)
        avg_color = color_counts.most_common(1)[0][0]
        average_ring = Ring(x=avg_x, y=avg_y, z=avg_z, area=avg_area, color=avg_color)
        logger.debug(f"Returning the AVG ring {average_ring}")
        return True, average_ring
    return False, None


def get_composite_calc_rings(rings):
    navigate_to_ring = get_short_or_longest_distance(rings, False)
    if (len(navigate_to_ring)) == 0:
        navigate_to_ring = get_avg_distance(rings)
        if (len(navigate_to_ring)) == 0:
            return False, navigate_to_ring
    return navigate_to_ring


def get_percentage_rings(rings, percent_to_discard, first_half):
    num_to_consider = int(len(rings) * (1 - percent_to_discard))
    if not first_half:
        return rings[-num_to_consider:]
    else:
        return rings[:-num_to_consider]


class Cv2CapReaderWriter:
    def __init__(self, write_vid=True):
        # buffer = int(25 * 1024 * 1024)
        # buffer_str = str(buffer)
        self.drone_video_url = 'udp://@0.0.0.0:11111?overrun_nonfatal=1'
        self.cap = cv2.VideoCapture(self.drone_video_url)
        self.cap.set(cv2.CAP_PROP_FPS, drone_types.FPS30)
        self.write_vid = write_vid
        if self.write_vid:
            self.writer = self.create_writer()

    def create_writer(self) -> cv2.VideoWriter:
        ret, frame = self.get_frame()
        out_writer: VideoWriter
        if ret:
            height, width, _ = frame.shape
            current_time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_video_path = f"./data/videos/test_run_{current_time_str}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (width, height))
            return out_writer

    def get_frame(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.drone_video_url)

        if not self.cap.isOpened():
            self.cap.open(self.drone_video_url)

        ret, frame = self.cap.read()
        if not ret:
            logger.error("Error: Couldn't read a frame from video.")
            return None, None
        return ret, frame

    def write(self, frame: np.ndarray):
        if self.write_vid:
            self.writer.write(frame)
        else:
            raise DroneException(message="attempting to write while no writer", code=DroneErrorCode.WriterError)

    def is_writeable(self):
        return self.write_vid

    def release(self):
        self.cap.release()


class DJIFrameRead:
    def __init__(self, drone):
        self.frame_read = drone.get_frame_read()

    def get_frame(self):
        ret, frame = self.frame_read.frame
        if not ret:
            logger.error("Error: Couldn't read a frame from video.")
            return None
        return frame


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
