import constants
from drone_types import Direction, Ring, NavigatorInput
from djitellopy import Tello
import plotter
import utils
from navigator.common import hover_time,adjust_drone_position_x, adjust_drone_position_y
from threading import Thread
import navigator
from arch_logger import logger


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello, cap_reader_writer) -> (bool, Ring):
    logger.info(f"navigating to ring {inn.ring_color} at position {inn.ring_position}")
    hover_time(1)
    '''
    if inn.ring_position == 0:
        logger.info(f"doing correction for ring position {inn.ring_position}")
        do_x_correction(cap_reader_writer, drone, inn, ring)
    '''
    distance_to_travel = ring.z + constants.buffer_distance
    logger.info(f"moving forward -- {distance_to_travel} =  {ring.z} + {constants.buffer_distance}")
    drone.move_forward(distance_to_travel)
    # hover_time(1)
    do_x_correction(cap_reader_writer, drone, inn, ring)
    return True, ring


def do_x_correction(cap_reader_writer, drone, inn, ring) -> Ring:
    x_direction, x_movement, next_ring = corrected_x(inn, ring, drone, cap_reader_writer)
    logger.info(f"moving {x_movement} {x_direction} for ring {inn.ring_position}")
    if x_direction == Direction.RIGHT:
        # adjust_drone_position_x(drone, x_movement, x_direction)
        drone.move_right(x_movement)
        return next_ring
    if x_direction == Direction.LEFT:
        # adjust_drone_position_x(drone, x_movement, x_direction)
        drone.move_left(x_movement)
        return next_ring
    return ring


# calculate x with new detection and determine corrected x
def corrected_x(inn: NavigatorInput, set_ring, drone, cap_read_writer) -> (Direction, int, Ring):
    right_left_threshold = constants.right_left_threshold
    inn.duration = 2
    attempts = 4
    deviation_x = 0
    drone_hover = Thread(target=navigator.common.hover_at, args=(inn, drone, attempts))
    drone_hover.start()
    rings_detected = plotter.plot(inn, cap_read_writer)
    drone_hover.join()

    logger.info(f"set ring -- {set_ring} for correction")
    detected, new_ring = utils.get_composite_calc_rings(rings_detected)
    logger.info(f"new ring {detected}")
    if detected:
        logger.info(f"new ring -- {new_ring} for correction")
        deviation_x = set_ring.x - new_ring.x
        logger.info(f"deviation x ---- {deviation_x}")
        direction_to_go = get_left_right_direction(deviation_x, right_left_threshold)
        return direction_to_go, deviation_x, new_ring
    return Direction.CENTER, deviation_x, new_ring


def get_left_right_direction(deviation_x, right_left_threshold) -> Direction:
    if 0 > deviation_x < -abs(right_left_threshold):
        logger.info(f"difference in set x and new ring is {deviation_x} moving to {Direction.LEFT}")
        return Direction.LEFT
    elif 0 < deviation_x > right_left_threshold:
        logger.info(f"difference in set x and new ring {deviation_x} moving to {Direction.RIGHT}")
        return Direction.RIGHT
    return Direction.CENTER


