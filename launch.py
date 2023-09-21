import config_loader
import plotter
from djitellopy import Tello
from navigator import simple
from drone_types import RingColor, Direction, DroneState, Ring, NavigatorInput
from threading import Thread
import queue
from typing import List


def drone_view():
    plotter.plot(False, False)


def ring_detected(r: Ring) -> (bool, Ring):
    if r.z == 0 or r.y == 0 or r.y == 0:
        return False, Ring
    return True, ring


def hover_and_detect_best(inn: NavigatorInput, ring_color: RingColor) -> (bool, Ring):
    attempts = 3
    is_detected = False
    rings_detected: List[Ring] = []
    r = Ring
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, drone, attempts))
        drone_hover.start()
        # detect and return ring
        r = Ring(x=100, y=40, z=180, area=4000, color=ring_color)
        # # detect and return ring
        drone_hover.join()
        if attempts != 0:
            attempts = attempts - 1
            rings_detected.append(r)
        else:
            break
    # find best ring code not complete
    return True, r


def hover_and_detect(inn: NavigatorInput, ring_color: RingColor) -> (bool, Ring):
    attempts = 3
    is_detected = False
    r: Ring
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, drone, attempts))
        drone_hover.start()
        # detect and return ring
        r = Ring(x=0, y=0, z=0, area=0, color=ring_color)
        # # detect and return ring
        drone_hover.join()
        if not ring_detected(r) and attempts != 0:
            attempts = attempts - 1
            is_detected = False
        else:
            return is_detected, r


# TODO add exception handling
if __name__ == '__main__':
    ring_sequence = [RingColor.YELLOW, RingColor.RED]
    config = config_loader.get_configurations()
    drone = Tello()
    drone.connect()
    drone.streamoff()
    drone.streamon()
    drone.takeoff()
    drone_state = DroneState
    q = queue.Queue()
    for ring in ring_sequence:
        hover_input = NavigatorInput(ring=ring,
                                     config=config,
                                     q=q,
                                     duration=10)
        detected, ring_data = hover_and_detect(hover_input, ring)
        if detected:
            simple.navigate_to(ring_data, drone)
    drone.land()
    drone.streamoff()
