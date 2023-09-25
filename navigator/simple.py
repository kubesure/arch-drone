from drone_types import Direction, RingColor, Ring, DroneState, NavigatorInput
from djitellopy import Tello
from time import sleep


def hover_at(inn: NavigatorInput, drone: Tello, attempt):
    print(f"attempt {attempt} on ring {inn.ring} with duration {inn.duration}")
    y_movement = 0
    y_direction = Direction.UP
    drone_height = drone.get_height()
    red_height = int(inn.config['red_optimum_hover_ht'])
    yellow_height = int(inn.config['yellow_optimum_hover_ht'])

    if inn.ring == RingColor.RED:
        print(f" red height {yellow_height} drone height {drone_height}")
        y_movement = red_height
        if drone_height > red_height:
            y_direction = Direction.DOWN
            y_movement = abs(drone_height - red_height)
        elif drone_height < red_height:
            y_direction = Direction.UP
            y_movement = abs(drone_height - red_height)
        print(f"y_direction {y_direction} y_movement {y_movement} ring {inn.ring}")
    elif inn.ring == RingColor.YELLOW:
        print(f" yellow height {yellow_height} drone height {drone_height}")
        y_movement = yellow_height
        if drone_height > yellow_height:
            y_direction = Direction.DOWN
            y_movement = abs(drone_height - yellow_height)
        elif drone_height < yellow_height:
            y_direction = Direction.UP
            y_movement = abs(drone_height - yellow_height)
        elif drone_height == yellow_height:
            y_direction = Direction.HOVER
        print(f"y_direction {y_direction} y_movement {y_movement} ring {inn.ring}")

    if y_direction == Direction.UP:
        drone.move_up(y_movement)
        print(f"moving up {y_movement} ring {inn.ring}")
    elif y_direction == Direction.DOWN:
        print(f"moving down {y_movement} ring {inn.ring}")
        drone.move_down(y_movement)
    elif y_direction == Direction.HOVER:
        print(f"direction hover")

    if attempt == 1:
        print(f"attempt {attempt} executing")
        hover(inn.duration)
    elif attempt == 2:
        print(f"attempt {attempt} executing")
        attempt_2_routine(drone)
    elif attempt == 3:
        print(f"attempt {attempt} executing")
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


def navigate_to(ring_data: Ring, drone) -> (bool, DroneState):
    print(f"moving forward {ring_data.z}")
    drone.move_forward(ring_data.z)
    return True, DroneState(last_ring_passed=ring_data)
