from drone_types import Direction, RingColor, Ring, DroneState, NavigatorInput
from djitellopy import Tello
from time import sleep
import time


def hover_at(inn: NavigatorInput, drone: Tello, attempt):
    print(f"attempt {attempt} on ring {inn.ring} with duration {inn.duration}")

    hover_at_optimum_height(drone, inn)

    if attempt == 1:
        print(f"attempt {attempt} executing scan")
        hover(inn.duration)
    elif attempt == 2:
        print(f"attempt {attempt} executing scan")
        attempt_2_routine(drone)
    elif attempt == 3:
        print(f"attempt {attempt} executing scan")
        attempt_3_routine(drone)


def hover_at_optimum_height(drone, inn):
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
    drone.move_right(15)
    hover(2)
    drone.move_left(30)
    hover(2)
    drone.move_right(15)
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


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello) -> (bool, DroneState):
    print(f"moving forward {ring.z} at speed {drone.get_speed_z()}")
    drone.go_xyz_speed(ring.x, ring.y, ring.z, 50)
    return True, DroneState(last_ring_passed=ring)


def navigate_n_correct_to(inn: NavigatorInput, ring: Ring, drone: Tello):
    forward_speed = int(inn.config['speed'])

    pid_x = PIDController(0, 0, 1)
    pid_y = PIDController(0, 0, 1)

    while True:

        # get current x y from detection
        set_ring = Ring(x=34, y=90, z=350, area=4500, color=RingColor.YELLOW)
        new_ring = Ring(x=34, y=90, z=350, area=4500, color=RingColor.YELLOW)

        # Calculate PID outputs for x and y
        set_point_x = set_ring.x
        set_point_y = set_ring.y

        current_x = new_ring.x
        current_y = new_ring.y

        output_x = pid_x.compute(set_point_x, current_x)
        output_y = pid_y.compute(set_point_y, current_y)

        final_x_velocity = output_x
        final_y_velocity = output_y
        final_forward_velocity = forward_speed
        drone.send_rc_control(final_x_velocity, final_forward_velocity, final_y_velocity, 0)

        time.sleep(1)
        # TODO break logic to be defined
        if 1 == 1:
            break
    return True, DroneState(last_ring_passed=ring)
