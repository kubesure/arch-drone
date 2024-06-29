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
import os


def ring_detected(r: Ring) -> (bool, Ring):
    """
    Check if the ring is detected based on its coordinates.

    Parameters:
    r (Ring): The ring object to check.

    Returns:
    tuple: A boolean indicating detection status and the ring object.
    """
    if r.z == 0 or r.y == 0 or r.x == 0:
        return False, r
    return True, r


def filter_zero_distances(rings: List[Ring]) -> List[Ring]:
    """
    Filter out rings with zero distances.

    Parameters:
    rings (List[Ring]): List of rings to filter.

    Returns:
    List[Ring]: List of rings with non-zero distances.
    """
    rings_detected: List[Ring] = []
    for ring in rings:
        if ring_detected(ring)[0]:
            rings_detected.append(ring)
    return rings_detected


def filter_distance(rings: List[Ring], distance: int) -> List[Ring]:
    """
    Filter rings based on a maximum distance.

    Parameters:
    rings (List[Ring]): List of rings to filter.
    distance (int): Maximum distance to filter by.

    Returns:
    List[Ring]: List of rings within the specified distance.
    """
    rings_dist_filter: List[Ring] = []
    for ring in rings:
        if ring.z < distance:
            rings_dist_filter.append(ring)
    return rings_dist_filter


def get_short_or_longest_distance(rings: List[Ring], longest: bool) -> (bool, Ring):
    """
    Get the ring with the shortest or longest distance.

    Parameters:
    rings (List[Ring]): List of rings to consider.
    longest (bool): Flag indicating whether to get the longest distance.

    Returns:
    tuple: A boolean indicating success and the ring with the desired distance.
    """
    logger.debug(f"Finding short or long ring out of rings {len(rings)}")

    rings = filter_zero_distances(rings)
    logger.debug(f"Ring for long short after filter {len(rings)}")

    rings = filter_distance(rings, constants.max_distance_btw_rings)
    logger.debug(f"Rings for percentage {rings}")

    if len(rings) == 0:
        return False, None
    sorted_rings = sorted(rings, key=lambda ring: ring.z, reverse=longest)
    return True, sorted_rings[0]


def get_avg_distance(rings: List[Ring]) -> (bool, Ring):
    """
    Calculate the average distance of the detected rings.

    Parameters:
    rings (List[Ring]): List of rings to consider.

    Returns:
    tuple: A boolean indicating success and the ring with average distance.
    """
    rings = filter_zero_distances(rings)
    max_distance_btw_rings = constants.max_distance_btw_rings
    logger.debug(f"Max distance between rings in get avg distance {max_distance_btw_rings}")
    rings = filter_distance(rings, max_distance_btw_rings)
    logger.debug(f"Rings for percentage {rings}")

    rings_to_consider = get_percentage_rings(rings, .50, True)
    logger.debug(f"Total rings {len(rings)} rings considered for avg {len(rings_to_consider)}")
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


def get_composite_calc_rings(rings: List[Ring]) -> (bool, Ring):
    """
    Get the ring with the shortest or longest distance or the average ring.

    Parameters:
    rings (List[Ring]): List of rings to consider.

    Returns:
    tuple: A boolean indicating success and the selected ring.
    """
    navigate_to_ring = get_short_or_longest_distance(rings, False)
    if not navigate_to_ring[0]:
        navigate_to_ring = get_avg_distance(rings)
        if not navigate_to_ring[0]:
            return False, navigate_to_ring
    return navigate_to_ring


def get_percentage_rings(rings: List[Ring], percent_to_discard: float, first_half: bool) -> List[Ring]:
    """
    Get a percentage of the rings.

    Parameters:
    rings (List[Ring]): List of rings to consider.
    percent_to_discard (float): Percentage of rings to discard.
    first_half (bool): Flag indicating whether to get the first or last percentage.

    Returns:
    List[Ring]: The selected percentage of rings.
    """
    num_to_consider = int(len(rings) * (1 - percent_to_discard))
    if not first_half:
        return rings[-num_to_consider:]
    else:
        return rings[:-num_to_consider]


class Cv2CapReaderWriter:
    """
    Class to handle video capture and writing using OpenCV.

    Attributes:
    drone_video_url (str): URL for the drone video stream.
    cap (cv2.VideoCapture): OpenCV VideoCapture object.
    write_vid (bool): Flag indicating whether to write video.
    writer (cv2.VideoWriter): OpenCV VideoWriter object.
    """

    def __init__(self, write_vid=True):
        self.drone_video_url = 'udp://@0.0.0.0:11111?overrun_nonfatal=1'
        self.cap = cv2.VideoCapture(self.drone_video_url)
        self.cap.set(cv2.CAP_PROP_FPS, drone_types.FPS30)
        self.write_vid = write_vid
        if self.write_vid:
            self.writer = self.create_writer()

    def create_writer(self) -> cv2.VideoWriter:
        """
        Create a video writer for saving the video stream.

        Returns:
        cv2.VideoWriter: OpenCV VideoWriter object.
        """
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
        """
        Capture a frame from the video stream.

        Returns:
        tuple: A boolean indicating success and the captured frame.
        """
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
        """
        Write a frame to the video file.

        Parameters:
        frame (np.ndarray): The frame to write.

        Raises:
        DroneException: If writing is attempted without an initialized writer.
        """
        if self.write_vid:
            self.writer.write(frame)
        else:
            raise DroneException(message="Attempting to write while no writer", code=DroneErrorCode.WriterError)

    def is_writeable(self):
        """
        Check if the video writer is writeable.

        Returns:
        bool: True if writeable, False otherwise.
        """
        return self.write_vid

    def release(self):
        """
        Release the video capture and writer resources.
        """
        self.cap.release()


class DJIFrameRead:
    """
    Class to handle frame reading from DJI drones.

    Attributes:
    frame_read: Frame read object from the drone.
    """

    def __init__(self, drone):
        self.frame_read = drone.get_frame_read()

    def get_frame(self):
        """
        Get the current frame from the drone's video feed.

        Returns:
        np.ndarray: The current frame.
        """
        frame = self.frame_read.frame
        if frame is None:
            logger.error("Error: Couldn't read a frame from video.")
            return None
        return frame


class DroneException(Exception):
    """
    Custom exception class for handling drone-specific errors.

    Attributes:
    message (str): Error message.
    error_code (DroneErrorCode): Error code.
    """

    def __init__(self, message="Internal error occurred", code=DroneErrorCode.InternalError):
        self.message = message
        self.error_code = code
