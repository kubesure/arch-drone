import config_loader
from djitellopy import Tello
from navigator import simple
from drone_types import RingColor, Ring, NavigatorInput, DroneErrorCode
from threading import Thread
import queue
from typing import List
import plotter
from utils import DroneException
import utils


def hover_and_detect_best(inn: NavigatorInput, dronee) -> (bool, Ring):
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, dronee, attempts))
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
        drone_hover = Thread(target=simple.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        rings_detected = plotter.plot(True, True, inn.duration, inn.ring, dronee)
        print(f"Rings detected {rings_detected}")
        drone_hover.join()
        if attempts == 1:
            break
    return utils.get_avg_distance(rings_detected)


# TODO add exception handling
if __name__ == '__main__':
    drone = Tello()

    try:
        ring_sequence = [RingColor.YELLOW, RingColor.YELLOW]
        config = config_loader.get_configurations()
        drone.connect()
        drone.set_video_fps(drone.FPS_30)
        drone.streamoff()
        drone.streamon()
        if drone.get_battery() < 2.5:
            print(f"battery not charged enough")
            drone.end()
        else:
            drone.takeoff()
            if not drone.is_flying:
                raise DroneException("Take off error", DroneErrorCode.TakeOffError)
            q = queue.Queue()
            for ring in ring_sequence:
                print(f"hovering for ring {ring}")
                hover_input = NavigatorInput(ring=ring,
                                             config=config,
                                             q=q,
                                             duration=8)
                detected, ring_data = hover_and_detect_avg_distance(hover_input, drone)
                if detected:
                    print(f"ring detected {ring_data}")
                    done_q = queue.Queue()
                    done_q.put(False)
                    drone_move_vid = Thread(target=utils.record_navigation, args=(done_q, True))
                    drone_move_vid.start()
                    simple.navigate_to(hover_input, ring_data, drone)
                    done_q.put(True)
                    drone_move_vid.join()
            drone.end()
    except DroneException as de:
        drone.end()
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Signalling main thread to land drone in emergency")
        drone.emergency()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        drone.end()
