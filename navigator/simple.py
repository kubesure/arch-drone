from drone_types import Direction, Ring, NavigatorInput
from djitellopy import Tello
import plotter
import utils
from navigator.common import get_optimum_hover_height, move_to_y, hover
from threading import Thread
import navigator
from arch_logger import logger


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello) -> bool:
    speed = int(inn.config['speed'])
    drone.set_speed(speed)
    distance_to_travel = ring.z + 25
    distance_travelled = 0
    incremental_distance = round(abs(distance_to_travel / 2))

    logger.info(f"distance to travel {distance_to_travel} distance travelled {distance_travelled}")
    while distance_to_travel > distance_travelled:
        # Forward
        logger.info(f"moving forward {incremental_distance}")
        if incremental_distance < 10:
            incremental_distance = incremental_distance + 25
        drone.move_forward(incremental_distance)
        distance_travelled = distance_travelled + incremental_distance
        logger.info(f"distance to travel left {distance_to_travel - distance_travelled}")
        hover(2)

        # Up Down
        y_direction, y_movement = get_optimum_hover_height(drone, inn)
        logger.info(f"hover to y direction {y_direction} y_movement {y_movement}")
        move_to_y(drone, inn, y_direction, y_movement)
        hover(2)

        # Left Right
        x_direction, x_movement, _ = corrected_x(inn, ring, drone)
        logger.info(f"moving to corrected x {x_movement} direction {x_direction}")
        if x_direction != Direction.CENTER:
            if x_movement > 0 and x_direction == Direction.RIGHT:
                logger.info(f"moving to corrected x {x_movement} direction {x_direction}")
                drone.move_right(x_movement)
                hover(2)
            if x_movement > 0 and x_direction == Direction.LEFT:
                logger.info(f"moving to corrected x {x_movement} direction {x_direction}")
                drone.move_left(x_movement)
                hover(2)
    return True


# calculate x with new detection and determine corrected x
def corrected_x(inn: NavigatorInput, set_ring, drone) -> (Direction, int, Ring):
    direction_to_go = Direction.CENTER
    inn.duration = 4
    attempts = 1
    drone_hover = Thread(target=navigator.common.hover_at, args=(inn, drone, attempts))
    drone_hover.start()
    rings_detected = plotter.plot(False, True, inn.duration, inn.ring, drone)
    drone_hover.join()

    new_ring = utils.get_avg_distance(rings_detected)

    deviation_x = new_ring.x - set_ring.x
    logger.info(f"deviation x {deviation_x}")

    if deviation_x > 0:
        direction_to_go = Direction.RIGHT
        logger.info(f"difference in current x and frame width {deviation_x} moving to {direction_to_go}")
    elif deviation_x < 0:
        direction_to_go = Direction.LEFT
        logger.info(f"difference in current x and frame width {deviation_x} moving to {direction_to_go}")
    elif deviation_x == 0:
        direction_to_go = Direction.CENTER
    return direction_to_go, deviation_x, new_ring

