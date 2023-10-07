from drone_types import Direction, Ring, NavigatorInput
from djitellopy import Tello
import plotter
import utils
from navigator.common import get_optimum_hover_height, move_to_y, hover
from threading import Thread
import navigator
from arch_logger import logger


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello, cap_reader_writer) -> (bool, Ring):
    speed = int(inn.config['speed'])
    drone.set_speed(speed)
    hover(1)
    distance_to_travel = ring.z + 5
    logger.info(f"moving forward -- {distance_to_travel}")
    do_x_correction(cap_reader_writer, drone, inn, ring)
    hover(2)
    logger.info(f"forward {int(distance_to_travel)}")
    # response = drone.send_command_with_return(f"forward {int(distance_to_travel)}")
    # logger.info(f"forward response {response}")
    drone.move_forward(distance_to_travel)
    hover(2)
    do_x_correction(cap_reader_writer, drone, inn, ring)
    return True, ring


def do_x_correction(cap_reader_writer, drone, inn, ring):
    x_direction, x_movement, next_ring = corrected_x(inn, ring, drone, cap_reader_writer)
    if x_direction != Direction.CENTER:
        if x_movement > 0 and x_direction == Direction.RIGHT:
            logger.info(f"moving to corrected x ---- {x_movement} direction {x_direction}")
            drone.move_right(x_movement)
            hover(2)
        if x_movement > 0 and x_direction == Direction.LEFT:
            logger.info(f"moving to corrected x ---- {x_movement} direction {x_direction}")
            drone.move_left(x_movement)
            hover(2)


# calculate x with new detection and determine corrected x
def corrected_x(inn: NavigatorInput, set_ring, drone, cap_read_writer) -> (Direction, int, Ring):
    direction_to_go = Direction.CENTER
    right_left_threshold = int(inn.config['right_left_threshold'])
    inn.duration = 3
    attempts = 4
    max_distance_btw_rings = int(inn.config['max_distance_btw_rings'])
    # logger.info(f"max_distance_btw_rings {max_distance_btw_rings}")
    drone_hover = Thread(target=navigator.common.hover_at, args=(inn, drone, attempts))
    drone_hover.start()
    rings_detected = plotter.plot(inn, cap_read_writer)
    drone_hover.join()

    logger.info(f"set ring -- {set_ring} in correction")
    detected, new_ring = utils.get_avg_distance(rings_detected, max_distance_btw_rings)
    logger.info(f"new ring in -- {new_ring} in correction")

    deviation_x = new_ring.x - set_ring.x
    logger.info(f"deviation x ---- {deviation_x}")

    if 0 > deviation_x > right_left_threshold:
        direction_to_go = Direction.RIGHT
        logger.info(f"difference in current x and frame width {deviation_x} moving to {direction_to_go}")
    elif 0 < deviation_x > right_left_threshold:
        direction_to_go = Direction.LEFT
        logger.info(f"difference in current x and frame width {deviation_x} moving to {direction_to_go}")
    return direction_to_go, deviation_x, new_ring


def move_x_incremental(drone: Tello, distance, direction: Direction):
    increment = abs(int(distance / 2))
    distance_covered = 0
    while distance > distance_covered:
        if direction == Direction.LEFT:
            drone.move_left(increment)
        if direction == Direction.RIGHT:
            drone.move_right(increment)
        distance_covered = increment + distance_covered
