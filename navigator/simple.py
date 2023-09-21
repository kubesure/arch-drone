from drone_types import Direction, RingColor, Ring, DroneState, NavigatorInput
from djitellopy import Tello
from time import sleep


def hover_at(inn: NavigatorInput, drone: Tello, attempt):
    y_movement = 0
    y_direction = Direction.UP
    drone_height = drone.get_height()
    red_height = inn.config['yellow_optimum_hover_ht']
    yellow_height = inn.config['red_optimum_hover_ht']

    if inn.ring == RingColor.RED:
        if drone_height > red_height:
            y_direction = Direction.DOWN
        elif drone_height < red_height:
            y_direction = Direction.UP
        y_movement = abs(drone_height - red_height)
    elif inn.ring == RingColor.YELLOW:
        if drone_height > yellow_height:
            y_direction = Direction.DOWN
        elif drone_height < yellow_height:
            y_direction = Direction.UP
        y_movement = abs(drone_height - yellow_height)

    if y_direction == Direction.UP:
        drone.move_up(y_movement)
    elif y_direction == Direction.DOWN:
        drone.move_down(y_movement)

    if attempt == 1:
        hover(inn.duration)
    elif attempt == 2:
        attempt_2_routine(drone)
    elif attempt == 3:
        attempt_3_routine(drone)


def hover(duration):
    hover_time = duration
    while True:
        sleep(1)
        hover_time = hover_time - 1
        if hover_time == 0:
            break


def attempt_2_routine(drone):
    drone.move_forward(30)
    hover(2)
    drone.rotate_clockwise(15)
    hover(2)
    drone.rotate_counter_clockwise(30)
    hover(2)
    drone.rotate_clockwise(15)
    hover(2)


def attempt_3_routine(drone):
    drone.move_back(30)
    hover(2)
    drone.move_up(20)
    hover(2)
    drone.rotate_clockwise(15)
    hover(2)
    drone.rotate_counter_clockwise(30)
    hover(2)
    drone.rotate_clockwise(15)
    hover(2)


def navigate_to(ring_data: Ring, drone: Tello) -> (bool, DroneState):
    drone.go_xyz_speed(ring_data.x, ring_data.y, ring_data.z, 20)
    # drone.move_forward(ring_data.z)
    return True, DroneState(last_ring_passed=ring_data)
