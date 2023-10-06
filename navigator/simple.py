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
    drone.move_forward(distance_to_travel)
    hover(2)
    x_direction, x_movement, _ = corrected_x(inn, ring, drone, cap_reader_writer)
    if x_direction != Direction.CENTER:
        if x_movement > 0 and x_direction == Direction.RIGHT:
            logger.info(f"moving to corrected x ---- {x_movement} direction {x_direction}")
            drone.move_right(x_movement)
            hover(2)
        if x_movement > 0 and x_direction == Direction.LEFT:
            logger.info(f"moving to corrected x ---- {x_movement} direction {x_direction}")
            drone.move_left(x_movement)
            hover(2)
    return True, ring


# calculate x with new detection and determine corrected x
def corrected_x(inn: NavigatorInput, set_ring, drone, cap_read_writer) -> (Direction, int, Ring):
    direction_to_go = Direction.CENTER
    right_left_threshold = int(inn.config['right_left_threshold'])
    inn.duration = 4
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

    if 0 > deviation_x:
        direction_to_go = Direction.RIGHT
        logger.info(f"difference in current x and frame width {deviation_x} moving to {direction_to_go}")
    elif 0 < deviation_x:
        direction_to_go = Direction.LEFT
        logger.info(f"difference in current x and frame width {deviation_x} moving to {direction_to_go}")
    return direction_to_go, deviation_x, new_ring
