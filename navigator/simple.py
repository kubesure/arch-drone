from drone_types import Direction, Ring, NavigatorInput
from djitellopy import Tello
import plotter
import utils
from navigator.common import get_optimum_hover_height, hover_to_y


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello) -> bool:
    print(f"moving forward {ring.z}")
    drone.set_speed(int(inn.config['speed']))
    distance_to_travel = ring.z + 20
    distance_travelled = 0
    incremental_distance = round(abs(distance_to_travel / 2))

    while distance_to_travel < distance_travelled:
        drone.move_forward(incremental_distance)
        distance_travelled = distance_travelled + incremental_distance
        y_direction, y_movement = get_optimum_hover_height(drone, inn)
        hover_to_y(drone, inn, y_direction, y_movement)
        x_direction, x_movement = corrected_xy(inn, ring, drone)
        if x_movement > 0 and x_direction == Direction.RIGHT:
            drone.move_right(x_movement)
        if x_movement > 0 and x_direction == Direction.LEFT:
            drone.move_left(x_movement)
    return True


# calculate x with new detection and determine corrected x
def corrected_xy(inn: NavigatorInput, set_ring, drone) -> (Direction, int):

    rings_detected = plotter.plot(False, True, inn.duration, inn.ring, drone)
    new_ring = utils.get_avg_distance(rings_detected)
    direction_to_go = Direction.FORWARD


    diff_x = {int(new_ring.bounding_width / 2) - new_ring.x}
    diff_y = {int(new_ring.bounding_height / 2) - new_ring.y}

    if new_ring.x < diff_x:
        direction_to_go = Direction.RIGHT
        print(f"difference in current x and bounding width {diff_x} moving to {direction_to_go}")
    elif new_ring.x > diff_x:
        direction_to_go = Direction.LEFT
        print(f"difference in current x and bounding width {diff_x} moving to {direction_to_go}")

    return direction_to_go, new_ring.x
