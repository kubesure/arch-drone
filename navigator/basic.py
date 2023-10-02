from drone_types import NavigatorInput, Ring
from djitellopy import Tello


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello) -> bool:
    print(f"moving forward {ring.z}")
    drone.set_speed(int(inn.config['speed']))
    distance_to_travel = 150 + 20
    drone.move_forward(distance_to_travel)
    return True
