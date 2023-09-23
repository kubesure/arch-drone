import config_loader
from djitellopy import Tello
from navigator import simple
from drone_types import RingColor, DroneState, Ring, NavigatorInput
from threading import Thread
import queue
from typing import List
import plotter
from mocktello import MockTello


def ring_detected(r: Ring) -> (bool, Ring):
    if r.z == 0 or r.y == 0 or r.y == 0:
        return False, Ring
    return True, ring


def hover_and_detect_best(inn: NavigatorInput, dronee) -> (bool, Ring):
    attempts = 3
    is_detected = False
    rings_detected: List[Ring] = []
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        # detect and return ring
        rings = plotter.plot(False, True, inn.duration, inn.ring)
        # rings = plotter.mock_plot(False, True, 10, inn.ring)
        # detect and return ring
        drone_hover.join()
        if attempts != 0:
            attempts = attempts - 1
            rings_detected.append(rings)
        else:
            break
        # find best ring code not complete
    return True, Ring(x=34, y=45, z=150, area=0, color=inn.ring)


def hover_and_detect(inn: NavigatorInput, dronee) -> (bool, Ring):
    attempts = 1
    is_detected = False
    r: Ring
    while not is_detected:
        drone_hover = Thread(target=simple.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()
        # detect and return ring
        if attempts < 4:
            r = Ring(x=0, y=0, z=0, area=0, color=inn.ring)
        else:
            r = Ring(x=34, y=45, z=150, area=0, color=inn.ring)
        # # detect and return ring
        drone_hover.join()
        if not ring_detected(r) and attempts < 4:
            is_detected = False
        else:
            is_detected = True
            return is_detected, r


# TODO add exception handling
if __name__ == '__main__':
    ring_sequence = [RingColor.YELLOW, RingColor.RED, RingColor.YELLOW, RingColor.RED]
    config = config_loader.get_configurations()
    # drone = MockTello()
    drone = Tello()
    drone.get_frame_read()
    drone.connect()
    if drone.get_battery() < 20:
        print(f"battery not charged enough")
    else:
        drone.streamoff()
        drone.streamon()
        drone.takeoff()
        drone_state = DroneState
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
