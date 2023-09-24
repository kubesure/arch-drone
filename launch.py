import config_loader
from djitellopy import Tello
from navigator import simple
from drone_types import RingColor, Ring, NavigatorInput
from threading import Thread
import queue
from typing import List
import plotter


def ring_detected(r: Ring) -> (bool, Ring):
    if r.z == 0 or r.y == 0 or r.y == 0:
        return False, Ring
    return True, r


def get_last_detected(rings) -> (bool, Ring):
    if len(rings) == 0:
        return False, None
    elif not ring_detected(rings[len(rings)]):
        return False, None
    return True, rings[len(rings)]


def find_best(rings) -> (bool, Ring):
    best_ring = Ring
    for r in rings:
        best_ring = Ring(x=34, y=45, z=150, area=0, color=r.ring)
    return True, best_ring


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
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        # detect and return ring
        rings = plotter.plot(True, True, inn.duration, inn.ring, dronee)
        # # detect and return ring
        drone_hover.join()
        if not get_last_detected(rings) and attempts < 4:
            attempts = attempts + 1
        else:
            is_detected, get_last_detected(rings)


# TODO add exception handling
if __name__ == '__main__':
    ring_sequence = [RingColor.YELLOW, RingColor.RED, RingColor.YELLOW, RingColor.RED]
    config = config_loader.get_configurations()
    drone = Tello()
    drone.connect()
    if drone.get_battery() < 0:
        print(f"battery not charged enough")
    else:
        drone.takeoff()
        q = queue.Queue()
        for ring in ring_sequence:
            hover_input = NavigatorInput(ring=ring,
                                         config=config,
                                         q=q,
                                         duration=12)
            detected, ring_data = hover_and_detect_best(hover_input, drone)
            if detected:
                print(f"ring detected {detected} x: {ring_data.x} y {ring_data.y} z{ring_data.z}")
                simple.navigate_to(ring_data, drone)
        drone.land()
        drone.streamoff()
