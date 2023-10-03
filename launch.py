import config_loader
from djitellopy import Tello
import navigator.common
from navigator import simple, basic
from drone_types import RingColor, Ring, NavigatorInput, DroneErrorCode
from threading import Thread
import queue
from typing import List
import plotter
from utils import DroneException
import utils
from arch_logger import logger


def hover_and_detect_best(inn: NavigatorInput, dronee) -> (bool, Ring):
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []
    while not is_detected:
        drone_hover = Thread(target=navigator.common.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        rings = plotter.plot(True, True, inn.duration, inn.ring, dronee)
        rings_detected.append(rings)
        drone_hover.join()
        if attempts != 0:
            attempts = attempts + 1
            rings_detected.append(rings)
        elif attempts == 3:
            rings_detected.append(rings)
            break
    return utils.get_short_or_longest_distance(rings_detected, True)


def hover_and_detect_avg_distance(inn: NavigatorInput, dronee) -> (bool, Ring):
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []
    while not is_detected:
        drone_hover = Thread(target=navigator.common.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        rings_detected = plotter.plot(True, True, inn.duration, inn.ring, dronee)
        drone_hover.join()
        if attempts == 1:
            break
    return utils.get_avg_distance(rings_detected)


# TODO add exception handling
if __name__ == '__main__':
    drone = Tello()

    try:
        ring_sequence = [RingColor.YELLOW,RingColor.YELLOW]
        config = config_loader.get_configurations()
        drone.connect()
        drone.streamoff()
        drone.streamon()
        logger.info(f"battery percentage - {drone.get_battery()}")
        if drone.get_battery() < 50:
            logger.info(f"battery less than 50% will cause issues flight re-charge")
            drone.end()
        else:
            drone.takeoff()
            if not drone.is_flying:
                raise DroneException("Take off error", DroneErrorCode.TakeOffError)
            q = queue.Queue()
            for ring in ring_sequence:
                logger.info(f"hovering for ring {ring}")
                hover_input = NavigatorInput(ring=ring,
                                             config=config,
                                             q=q,
                                             duration=4)
                detected, ring_data = hover_and_detect_avg_distance(hover_input, drone)
                if detected:
                    logger.info(f"ring detected to navigate {ring_data}")
                    simple.navigate_to(hover_input, ring_data, drone)
            drone.end()
    except DroneException as de:
        logger.error(de.get_error_message())
        drone.end()
    except KeyboardInterrupt:
        logger.error("Ctrl+C pressed or process killed. Signalling main thread to land drone in emergency")
        drone.emergency()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        drone.end()
