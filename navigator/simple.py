from drone_types import Direction, RingColor, Ring, DroneState, NavigatorInput
from djitellopy import Tello
from time import sleep


def hover_and_detect(inn: NavigatorInput, drone: Tello):
    height = 0

    if inn.ring == RingColor.RED:
        height = inn.config['yellow_optimum_hover_ht']
    elif inn.ring == RingColor.YELLOW:
        height = inn.config['red_optimum_hover_ht']

    if inn.direction == Direction.UP:
        drone.move_up(height)
    elif inn.direction == Direction.DOWN:
        drone.move_down(height)

    drone.move_forward(30)
    drone.rotate_clockwise(15)
    drone.rotate_clockwise(30)
    drone.rotate_clockwise(15)
    drone.rotate_clockwise(15)
    hover = True
    hover_time = inn.duration
    ring: Ring

    while hover:
        sleep(1)
        hover_time = hover_time - 1
        if hover_time == 0:
            hover = False


def navigate_to(ring_data: Ring, drone: Tello) -> (bool, DroneState):
    drone.move_forward(ring_data.z)
    return True, DroneState(last_ring_passed=ring_data)
