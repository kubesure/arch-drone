import constants
from drone_types import Direction, Ring, NavigatorInput
from djitellopy import Tello
import plotter
import utils
from navigator.common import hover_time
from threading import Thread
import navigator
from arch_logger import logger


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello, cap_reader_writer) -> (bool, Ring):
    """
    Navigate the drone to the specified ring position.

    Parameters:
    inn (NavigatorInput): Input containing details about the target ring.
    ring (Ring): Current ring status and position.
    drone (Tello): Drone object to control movements.
    cap_reader_writer: Object to read and write frames to record the video of navigation.

    Returns:
    tuple: A tuple containing a boolean indicating success and the updated ring object.

    Process:
    1. Log the navigation start.
    2. Hover for a second to stabilize the drone.
    3. Calculate the distance to travel and log the information.
    4. Move the drone forward by the calculated distance.
    5. Perform x-axis correction.
    6. Return success status and the ring object.
    """
    logger.info(f"Navigating to ring {inn.ring_color} at position {inn.ring_position}")
    hover_time(1)  # Hover to stabilize the drone

    # Calculate the distance to travel
    distance_to_travel = ring.z + constants.buffer_distance
    logger.info(f"Moving forward -- {distance_to_travel} = {ring.z} + {constants.buffer_distance}")

    # Move the drone forward
    drone.move_forward(distance_to_travel)

    # Perform x-axis correction
    do_x_correction(cap_reader_writer, drone, inn, ring)

    return True, ring


def do_x_correction(cap_reader_writer, drone, inn, ring) -> Ring:
    """
    Perform x-axis correction to align the drone with the ring.

    Parameters:
    cap_reader_writer: Object to read and write frames to record the video of navigation.
    drone (Tello): Drone object to control movements.
    inn (NavigatorInput): Input containing details about the target ring.
    ring (Ring): Current ring status and position.

    Returns:
    Ring: Updated ring object after correction.
    """
    x_direction, x_movement, next_ring = corrected_x(inn, ring, drone, cap_reader_writer)
    logger.info(f"Moving {x_movement} {x_direction} for ring {inn.ring_position}")

    if x_direction == Direction.RIGHT:
        # Move the drone to the right
        drone.move_right(x_movement)
        return next_ring
    elif x_direction == Direction.LEFT:
        # Move the drone to the left
        drone.move_left(x_movement)
        return next_ring

    return ring


def corrected_x(inn: NavigatorInput, set_ring, drone, cap_read_writer) -> (Direction, int, Ring):
    """
    Calculate x-axis correction based on new ring detection.

    Parameters:
    inn (NavigatorInput): Input containing details about the target ring.
    set_ring (Ring): Current ring status and position.
    drone (Tello): Drone object to control movements.
    cap_reader_writer: Object to read and write frames to record the video of navigation.

    Returns:
    tuple: A tuple containing the direction to move, the deviation in x, and the updated ring object.
    """
    right_left_threshold = constants.right_left_threshold
    inn.duration = 2
    attempts = 4
    deviation_x = 0

    # Start a thread to hover the drone while detecting the ring
    drone_hover = Thread(target=navigator.common.hover_at, args=(inn, drone, attempts))
    drone_hover.start()

    # Detect rings and plot their positions
    rings_detected = plotter.plot(inn, cap_read_writer)
    drone_hover.join()

    logger.info(f"Set ring -- {set_ring} for correction")
    detected, new_ring = utils.get_composite_calc_rings(rings_detected)
    logger.info(f"New ring {detected}")

    if detected:
        logger.info(f"New ring -- {new_ring} for correction")
        deviation_x = set_ring.x - new_ring.x
        logger.info(f"Deviation x ---- {deviation_x}")

        # Determine the direction to move based on the deviation
        direction_to_go = get_left_right_direction(deviation_x, right_left_threshold)
        return direction_to_go, deviation_x, new_ring

    return Direction.CENTER, deviation_x, new_ring


def get_left_right_direction(deviation_x, right_left_threshold) -> Direction:
    """
    Determine the direction to move based on the deviation in x-axis.

    Parameters:
    deviation_x (int): Deviation in x-axis from the center.
    right_left_threshold (int): Threshold value to decide movement direction.

    Returns:
    Direction: Direction to move (LEFT, RIGHT, CENTER).
    """
    if 0 > deviation_x < -abs(right_left_threshold):
        logger.info(f"Difference in set x and new ring is {deviation_x}, moving to {Direction.LEFT}")
        return Direction.LEFT
    elif 0 < deviation_x > right_left_threshold:
        logger.info(f"Difference in set x and new ring {deviation_x}, moving to {Direction.RIGHT}")
        return Direction.RIGHT

    return Direction.CENTER
