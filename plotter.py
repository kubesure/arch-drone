from typing import List
from drone_types import Ring
from detector import contour
import time
from djitellopy import Tello
import utils
from arch_logger import logger


def plot(write_vid, detect: bool, duration, ring, drone: Tello):
    rings_detected: List[Ring] = []

    out_writer, video_reader = utils.get_out_writer(write_vid)

    if out_writer is None or video_reader is None:
        write_vid = False

    detector = contour.ContourFilter()
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        _, frame = video_reader.get_frame()

        if detect:
            r, detected_frame = detector.get_xyz_ring(frame, ring)
            frame = detected_frame
            rings_detected.append(r)
        if write_vid:
            out_writer.write(frame)

    if write_vid:
        out_writer.release()

    logger.info(f"Rings from detector {len(rings_detected)} - rings {rings_detected}")
    final_detected: List[Ring] = []
    for r in rings_detected:
        if utils.ring_detected(r):
            final_detected.append(r)
    logger.info(f"Final rings from plotter {len(final_detected)} - rings {final_detected}")
    return final_detected


def mock_plot(write_vid, detect: bool, duration, ring):
    rings_detected: List[Ring] = [Ring(x=34, y=45, z=150, area=0, color=ring)]
    return rings_detected
