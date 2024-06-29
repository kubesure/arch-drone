from detector import contour
import time
import utils
from arch_logger import logger
from drone_types import NavigatorInput


def plot(inn: NavigatorInput, cap_reader_writer):
    """
    Detect and plots the next rings in the video frames captured by the drone.

    Parameters:
    inn (NavigatorInput): Input containing details about the navigation.
    cap_reader_writer: Object to read and write video frames.

    Returns:
    list: A list of detected rings.

    Process:
    1. Initialize the contour detector and start the timer.
    2. Capture video frames within the specified duration.
    3. Detect rings in each frame and store the detected rings.
    4. Write frames if the cap_reader_writer is writeable.
    5. Filter and return the detected rings.
    6. Handle exceptions and log errors.
    """
    rings_detected = []
    detector = contour.ContourFilter()
    start_time = time.time()

    try:
        while int(time.time() - start_time) < inn.duration:
            # Capture a frame from the video stream
            _, frame = cap_reader_writer.get_frame()

            # Detect rings in the frame
            r, detected_frame = detector.get_xyz_ring(frame, inn.ring_color)
            frame = detected_frame

            # Store detected rings
            rings_detected.append(r)

            # Write the frame if the writer is writeable
            if cap_reader_writer.is_writeable():
                cap_reader_writer.write(frame)

        logger.debug(f"Rings from detector {len(rings_detected)} - rings {rings_detected}")

        final_detected = []
        for r in rings_detected:
            # Filter detected rings
            if utils.ring_detected(r):
                final_detected.append(r)

        logger.debug(f"Final rings from plotter {len(final_detected)} - rings {final_detected}")
        return final_detected
    except Exception as e:
        logger.error(f"An error occurred in plotter: {str(e)}")
        raise e
