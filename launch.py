import config_loader
from djitellopy import Tello
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


def hover_and_detect_avg_distance(inn: NavigatorInput, dronee, cap_read_write) -> (bool, Ring):
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []
    while not is_detected:
        drone_hover = Thread(target=navigator.common.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        rings_detected = plotter.plot(inn, cap_read_write)
        drone_hover.join()
        if attempts == 1:
            break
    return utils.get_avg_distance(rings_detected, inn)


# TODO add exception handling
if __name__ == '__main__':
    drone = Tello()

    try:
        ring_sequence = [RingColor.YELLOW, RingColor.YELLOW]
        config = config_loader.get_configurations()
        drone.connect()
        drone.streamoff()
        drone.streamon()
        cap_reader_writer = utils.Cv2CapReaderWriter()
        logger.info(f"battery percentage - {drone.get_battery()}")
        if drone.get_battery() < 40:
            logger.info(f"battery less than 50% will cause issues flight re-charge")
            drone.end()
        else:
            drone.takeoff()
            # navigator.common.hover(2)
            if not drone.is_flying:
                raise DroneException("Take off error", DroneErrorCode.TakeOffError)
            q = queue.Queue()
            last_ring_navigated = Ring(x=0, y=0, z=0, area=0, color=RingColor.YELLOW)
            for ring in ring_sequence:
                fly_input = NavigatorInput(ring_color=ring,
                                           config=config,
                                           q=q,
                                           duration=4,
                                           last_ring_navigated=last_ring_navigated)
                detected, ring = hover_and_detect_avg_distance(fly_input, drone, cap_reader_writer)
                if detected:
                    logger.info(f"ring detected navigate to {ring}")
                    navigated, last_navigated_ring = simple.navigate_to(fly_input, ring, drone, cap_reader_writer)
            cap_reader_writer.release()
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
