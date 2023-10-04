from detector import contour
import time
import utils
from arch_logger import logger


def plot(inn, cap_reader_writer):
    rings_detected = []
    detector = contour.ContourFilter()
    start_time = time.time()

    try:
        while int(time.time() - start_time) < inn.duration:
            _, frame = cap_reader_writer.get_frame()
            r, detected_frame = detector.get_xyz_ring(frame, inn.ring_color)
            frame = detected_frame
            rings_detected.append(r)
            if cap_reader_writer.is_writeable():
                cap_reader_writer.write(frame)

        logger.info(f"Rings from detector {len(rings_detected)} - rings {rings_detected}")
        final_detected = []
        for r in rings_detected:
            if utils.ring_detected(r):
                final_detected.append(r)
        logger.info(f"Final rings from plotter {len(final_detected)} - rings {final_detected}")
        return final_detected
    except Exception as e:
        logger.error(f"An error occurred in plotter: {str(e)}")
