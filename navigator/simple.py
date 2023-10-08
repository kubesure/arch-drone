import constants
from drone_types import Direction, Ring, NavigatorInput
from djitellopy import Tello
import plotter
import utils
from navigator.common import get_optimum_hover_height, hover_time
from threading import Thread
import navigator
from arch_logger import logger
import time


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello, cap_reader_writer) -> (bool, Ring):
    logger.info(f"navigating to ring {inn.ring_color} at position {inn.ring_position}")
    # speed = constants.speed
    # drone.set_speed(speed)
    hover_time(1)
    distance_to_travel = ring.z + 15
    logger.info(f"moving forward -- {distance_to_travel}")
    if inn.ring_position != 0:
        do_x_correction(cap_reader_writer, drone, inn, ring)
    drone.move_forward(distance_to_travel)
    hover_time(1)
    do_x_correction(cap_reader_writer, drone, inn, ring)
    return True, ring


def do_x_correction(cap_reader_writer, drone, inn, ring):
    x_direction, x_movement, next_ring = corrected_x(inn, ring, drone, cap_reader_writer)
    logger.info(f"direction received for correction {x_direction} x movement {x_movement}")
    if x_direction != Direction.CENTER:
        if x_movement > 0 and x_direction == Direction.RIGHT:
            logger.info(f"moving to corrected x ---- {x_movement} direction {x_direction}")
            drone.move_right(x_movement)
            hover_time(2)
        if x_movement > 0 and x_direction == Direction.LEFT:
            logger.info(f"moving to corrected x ---- {x_movement} direction {x_direction}")
            drone.move_left(x_movement)
            hover_time(2)


# calculate x with new detection and determine corrected x
def corrected_x(inn: NavigatorInput, set_ring, drone, cap_read_writer) -> (Direction, int, Ring):
    direction_to_go = Direction.CENTER
    right_left_threshold = constants.right_left_threshold
    inn.duration = 2
    attempts = 4
    deviation_x = 0
    drone_hover = Thread(target=navigator.common.hover_at, args=(inn, drone, attempts))
    drone_hover.start()
    rings_detected = plotter.plot(inn, cap_read_writer)
    drone_hover.join()

    logger.debug(f"set ring -- {set_ring} for correction")
    detected, new_ring = utils.get_composite_calc_rings(rings_detected)
    logger.debug(f"new ring {detected}")
    if detected:
        logger.debug(f"new ring in -- {new_ring} for correction")
        deviation_x = new_ring.x - set_ring.x
        logger.info(f"deviation x ---- {deviation_x}")

        if 0 > deviation_x > -abs(right_left_threshold):
            direction_to_go = Direction.RIGHT
            logger.info(f"difference in set x and new ring is {deviation_x} moving to {direction_to_go}")
        elif 0 < deviation_x > right_left_threshold:
            direction_to_go = Direction.LEFT
            logger.info(f"difference in set x and new ring {deviation_x} moving to {direction_to_go}")
    else:
        logger.info(f"no new rings detected for x deviation correction")
    return direction_to_go, deviation_x, new_ring


def move_left_for_distance(drone, distance_cm):
    speed = 20  # cm/s, you can adjust this
    travel_time = distance_cm / speed  # time = distance/speed

    drone.send_rc_control(-speed, 0, 0, 0)  # Move left
    time.sleep(travel_time)  # Wait for the drone to travel the desired distance
    drone.send_rc_control(0, 0, 0, 0)  # Stop the drone


def move_right_for_distance(drone, distance_cm):
    speed = 20  # cm/s, you can adjust this
    travel_time = distance_cm / speed  # time = distance/speed

    drone.send_rc_control(speed, 0, 0, 0)  # Move right
    time.sleep(travel_time)  # Wait for the drone to travel the desired distance
    drone.send_rc_control(0, 0, 0, 0)  # Stop the drone


def move_x_incremental(drone: Tello, distance, direction: Direction):
    increment = abs(int(distance / 2))
    distance_covered = 0
    while distance > distance_covered:
        if direction == Direction.LEFT:
            drone.move_left(increment)
        if direction == Direction.RIGHT:
            drone.move_right(increment)
        distance_covered = increment + distance_covered
