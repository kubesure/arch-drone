import config_loader
from djitellopy import Tello
from navigator import simple
from drone_types import RingColor, Ring, NavigatorInput
from threading import Thread
import queue
from typing import List
import plotter


def hover_and_detect_best(inn: NavigatorInput, dronee) -> (bool, Ring):
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        # detect and return ring
        rings = plotter.plot(True, True, inn.duration, inn.ring, dronee)
        rings_detected.append(rings)
        # detect
        drone_hover.join()
        if attempts != 0:
            attempts = attempts + 1
            rings_detected.append(rings)
        elif attempts == 3:
            rings_detected.append(rings)
            break
    return find_best(rings_detected)



def hover_and_detect_last_one(inn: NavigatorInput, dronee) -> (bool, Ring):
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        # detect and return ring
        rings = plotter.plot(True, True, inn.duration, inn.ring, dronee)
        rings_detected.append(rings)
        # # detect and return ring
        drone_hover.join()
        if attempts == 1:
            break
    return get_last_detected(rings_detected)


# TODO add exception handling
if __name__ == '__main__':
    drone = Tello()
    flying = False
    try:
        ring_sequence = [RingColor.RED]
        config = config_loader.get_configurations()
        drone.connect()
        if drone.get_battery() < 2.5:
            print(f"battery not charged enough")
        else:
            drone.takeoff()
            q = queue.Queue()
            for ring in ring_sequence:
                print(f"hovering for ring {ring}")
                hover_input = NavigatorInput(ring=ring,
                                             config=config,
                                             q=q,
                                             duration=10)
                detected, ring_data = hover_and_detect_last_one(hover_input, drone)
                if detected:
                    print(f"ring detected {detected} x: {ring_data.x} y {ring_data.y} z{ring_data.z}")
                    simple.navigate_to(ring_data, drone)
            drone.land()
            drone.streamoff()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        drone.land()
        drone.streamoff()
