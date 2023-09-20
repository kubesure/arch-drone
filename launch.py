from djitellopy import Tello
import config_loader
import plotter
from djitellopy import Tello
from navigator import simple
from drone_types import RingColor, Direction, DroneState, Ring, NavigatorInput
from threading import Thread
import queue


def drone_view():
    plotter.plot(False, False, None, 0)


def ring_detected(r: Ring) -> (bool, Ring):
    if r.z == 0 or r.y == 0 or r.y == 0:
        return False, Ring
    return True, ring


# TODO add exception handling
if __name__ == '__main__':
    ring_sequence = [RingColor.YELLOW, RingColor.RED]
    config = config_loader.get_configurations()
    drone = Tello()
    drone.set_speed(50)
    drone.connect()
    drone.streamoff()
    drone.streamon()

    drone_state = DroneState
    q = queue.Queue()
    for ring in ring_sequence:
        hover_input = NavigatorInput(ring=ring,
                                     direction=Direction.UP,
                                     config=config,
                                     q=q,
                                     duration=20)
        drone_hover = Thread(target=simple.hover_and_detect, args=(hover_input, drone))
        drone_hover.start()
        # detect and return ring
        ring_data = Ring(x=100, y=40, z=180, area=4000, color=ring)
        # # detect and return ring
        drone_hover.join()
        simple.navigate_to(ring_data, drone)

    drone.streamoff()
    drone.land()
