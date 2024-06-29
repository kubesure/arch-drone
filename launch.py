import config_loader
from djitellopy import Tello
import constants
import navigator.common
from navigator import simple
from drone_types import RingColor, Ring, NavigatorInput, DroneErrorCode
from threading import Thread
import queue
from typing import List
import plotter
from utils import DroneException
import utils
from arch_logger import logger


def hover_and_get_ring(inn: NavigatorInput, dronee, cap_read_write) -> (bool, Ring):
    """
    Hover the drone and detect rings in the surroundings.

    Parameters:
    inn (NavigatorInput): Input containing details about the navigation.
    dronee (Tello): Drone object to control movements.
    cap_read_write: Object to read and write data for ring detection.

    Returns:
    tuple: A tuple containing a boolean indicating detection success and the detected Ring object.

    Process:
    1. Initialize attempt count and detection status.
    2. Start a thread to hover the drone and detect rings.
    3. Plot detected rings and join the hover thread.
    4. Return the average distance of detected rings.

    The method hovers the drone at a specified position and captures video frames to detect rings.
    It then processes the detected rings to find the average position of all detected rings and returns
    the average ring's position and detection status.
    """
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []

    # Start a thread to hover the drone and detect rings
    while not is_detected:
        drone_hover = Thread(target=navigator.common.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()

        # Capture and plot the detected rings
        rings_detected = plotter.plot(inn, cap_read_write)
        drone_hover.join()

        if attempts == 1:
            break

    # Return the average distance of detected ring
    return utils.get_avg_distance(rings_detected)


def launch_and_navigate_drone():
    """
    Launch the drone, navigate through a sequence of rings, and handle any exceptions.

    Process:
    1. Initialize the drone and the cap reader/writer.
    2. Load configurations and connect to the drone.
    3. Check the battery level and handle accordingly.
    4. Start the drone flight sequence.
    5. Iterate through the ring sequence and navigate to each ring.
    6. Handle exceptions and ensure proper resource release.

    Raises:
    DroneException: Custom exception for handling specific drone errors.
    """
    drone = Tello()
    cap_reader_writer: utils.Cv2CapReaderWriter
    try:
        ring_sequence = [RingColor.YELLOW, RingColor.YELLOW, RingColor.YELLOW, RingColor.YELLOW,
                         RingColor.YELLOW, RingColor.YELLOW, RingColor.YELLOW, RingColor.YELLOW]

        # Load configurations and connect to the drone
        config_loader.get_configurations()
        drone.connect()
        drone.streamoff()
        drone.streamon()
        cap_reader_writer = utils.Cv2CapReaderWriter()
        logger.info(f"Battery percentage - {drone.get_battery()}")

        # Check battery level and handle accordingly
        if drone.get_battery() < 80:
            logger.info(f"Battery less than {drone.get_battery()}% will cause issues during flight, please recharge.")
            drone.end()
        else:
            # Start the drone flight sequence
            drone.takeoff()
            navigator.common.hover_time(1)
            drone.set_speed(constants.speed)
            if not drone.is_flying:
                raise DroneException("Take off error", DroneErrorCode.TakeOffError)

            q = queue.Queue()
            last_ring_navigated = Ring(x=0, y=0, z=0, area=0, color=RingColor.YELLOW)

            # Iterate through the ring sequence and navigate to each ring
            for index, ring in enumerate(ring_sequence):
                logger.info(f"Running sequence for ring color {ring} at index {index}")
                flight_input = NavigatorInput(ring_color=ring,
                                              q=q,
                                              duration=3,
                                              last_ring_navigated=last_ring_navigated,
                                              ring_position=index)
                detected, ring = hover_and_get_ring(flight_input, drone, cap_reader_writer)
                if detected:
                    logger.info(f"Ring detected, navigating to {ring}")
                    _, last_navigated_ring = simple.navigate_to(flight_input, ring, drone, cap_reader_writer)
                else:
                    logger.info("No rings detected")

            cap_reader_writer.release()
            drone.end()
    except DroneException as de:
        logger.error(de.get_error_message())
        cap_reader_writer.release()
        drone.end()
    except KeyboardInterrupt:
        logger.error("Ctrl+C pressed, landing or emergency landing")
        cap_reader_writer.release()
        drone.end()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        cap_reader_writer.release()
        drone.end()


if __name__ == '__main__':
    launch_and_navigate_drone()
