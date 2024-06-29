from time import sleep
from djitellopy import Tello
import time
import constants
from drone_types import NavigatorInput, Direction, RingColor
from arch_logger import logger


def hover_at(inn: NavigatorInput, drone: Tello, attempt):
    """
    Hover the drone at a specific height and perform scanning routines based on the attempt number.

    Parameters:
    inn (NavigatorInput): Input containing details about the navigation.
    drone (Tello): Drone object to control movements.
    attempt (int): The current attempt number for hovering and scanning.

    Process:
    1. Log the current attempt and ring color.
    2. Perform height adjustment for attempts other than 4.
    3. Execute different scanning routines based on the attempt number.
    """
    logger.debug(f"Attempt {attempt} on ring {inn.ring_color} with duration {inn.duration}")

    # TODO: Write exception handling since it's a thread inform main thread

    if attempt != 4:
        y_direction, y_movement = get_optimum_hover_height(drone, inn)
        move_to_y(drone, inn, y_direction, y_movement)

    if attempt == 1:
        logger.debug(f"Attempt {attempt} executing scan")
        hover_time(inn.duration)
    elif attempt == 2:
        logger.debug(f"Attempt {attempt} executing scan")
        attempt_2_routine(drone)
    elif attempt == 3:
        logger.debug(f"Attempt {attempt} executing scan")
        attempt_3_routine(drone)


def get_optimum_hover_height(drone, inn):
    """
    Determine the optimal hover height for the drone based on the ring color.

    Parameters:
    drone (Tello): Drone object to control movements.
    inn (NavigatorInput): Input containing details about the navigation.

    Returns:
    tuple: A tuple containing the direction to move and the distance to move in the y-axis.
    """
    y_movement = 0
    y_direction = Direction.UP
    drone_height = drone.get_height()
    red_height = constants.red_optimum_hover_ht
    yellow_height = constants.yellow_optimum_hover_ht

    if inn.ring_color == RingColor.RED:
        logger.info(f"Red height {red_height} drone height {drone_height}")
        y_movement = red_height
        if drone_height > red_height:
            y_direction = Direction.DOWN
            y_movement = abs(drone_height - red_height)
        elif drone_height < red_height:
            y_direction = Direction.UP
            y_movement = abs(drone_height - red_height)
        logger.debug(f"y_direction {y_direction} y_movement {y_movement} ring {inn.ring_color}")

    elif inn.ring_color == RingColor.YELLOW:
        logger.info(f"Yellow height {yellow_height} drone height {drone_height}")
        y_movement = yellow_height
        if drone_height > yellow_height:
            y_direction = Direction.DOWN
            y_movement = abs(drone_height - yellow_height)
        elif drone_height < yellow_height:
            y_direction = Direction.UP
            y_movement = abs(drone_height - yellow_height)
        elif drone_height == yellow_height:
            y_direction = Direction.HOVER
        logger.debug(f"y_direction {y_direction} y_movement {y_movement} ring {inn.ring_color}")

    return y_direction, y_movement


def move_to_y(drone, inn, y_direction, y_movement):
    """
    Move the drone in the y-axis based on the direction and distance.

    Parameters:
    drone (Tello): Drone object to control movements.
    inn (NavigatorInput): Input containing details about the navigation.
    y_direction (Direction): The direction to move in the y-axis (UP, DOWN, HOVER).
    y_movement (int): The distance to move in the y-axis.
    """
    threshold = constants.hover_up_down_threshold

    if y_direction == Direction.UP:
        logger.info(f"Moving up {y_movement} ring {inn.ring_color}")
        if y_movement > threshold:
            drone.move_up(y_movement)
    elif y_direction == Direction.DOWN:
        logger.info(f"Moving down {y_movement} ring {inn.ring_color}")
        if y_movement > threshold:
            drone.move_down(y_movement)
    elif y_direction == Direction.HOVER:
        logger.info(f"Hovering at height {drone.get_height()}")


class PIDController:
    """
    A PID controller for computing the control variable based on proportional, integral, and derivative terms.

    Attributes:
    kp (float): Proportional gain.
    ki (float): Integral gain.
    kd (float): Derivative gain.
    prev_error (float): Previous error value.
    integral (float): Integral of the error.
    """

    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        """
        Compute the control variable based on the error.

        Parameters:
        error (float): The current error value.

        Returns:
        float: The computed control variable.
        """
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output


def adjust_drone_position_z(drone, difference, direction):
    """
    Adjust the drone's position in the z-axis (forward/backward) using a PID controller.

    Parameters:
    drone (Tello): Drone object to control movements.
    difference (float): The distance to adjust.
    direction (Direction): The direction to move (FORWARD, BACKWARD).
    """
    pid = PIDController(0.50, 0.50, 0.00)
    velocity = pid.compute(difference)
    logger.info(f"Velocity from PID controller {velocity}")

    if direction == Direction.FORWARD:
        logger.info(f"RC command {direction}")
        drone.send_rc_control(0, int(velocity), 0, 0)
        logger.info(f"Sleep time {abs(difference) / velocity}")
        time.sleep(abs(difference) / velocity)
        drone.send_rc_control(0, 0, 0, 0)
    elif direction == Direction.BACKWARD:
        logger.info(f"RC command {direction}")
        drone.send_rc_control(-int(velocity), 0, 0, 0)
        logger.info(f"Sleep time {abs(difference) / velocity}")
        time.sleep(abs(difference) / velocity)
        drone.send_rc_control(0, 0, 0, 0)


def adjust_drone_position_x(drone, difference, direction):
    """
    Adjust the drone's position in the x-axis (left/right) using a PID controller.

    Parameters:
    drone (Tello): Drone object to control movements.
    difference (float): The distance to adjust.
    direction (Direction): The direction to move (LEFT, RIGHT).
    """
    pid = PIDController(0.50, 0.50, 0.00)
    velocity = pid.compute(difference)
    logger.info(f"Velocity from PID controller {velocity}")

    if direction == Direction.LEFT:
        logger.info(f"RC command {direction}")
        drone.send_rc_control(-int(velocity), 0, 0, 0)
        logger.info(f"Sleep time {abs(difference) / velocity}")
        time.sleep(1.25)
        drone.send_rc_control(0, 0, 0, 0)
    else:
        logger.info(f"RC command {direction}")
        drone.send_rc_control(int(velocity), 0, 0, 0)
        logger.info(f"Sleep time {abs(difference) / velocity}")
        time.sleep(1.25)
        drone.send_rc_control(0, 0, 0, 0)


def adjust_drone_position_y(drone, difference, direction):
    """
    Adjust the drone's position in the y-axis (up/down) using a PID controller.

    Parameters:
    drone (Tello): Drone object to control movements.
    difference (float): The distance to adjust.
    direction (Direction): The direction to move (UP, DOWN).
    """
    if direction == Direction.UP:
        pid = PIDController(0.7, 0.7, 0.00)
        velocity = pid.compute(difference)
        logger.info(f"Velocity by PID {velocity}")
        drone.send_rc_control(0, 0, int(velocity), 0)
        logger.info(f"Sleep time {abs(difference) / velocity}")
        time.sleep(2.5)
        drone.send_rc_control(0, 0, 0, 0)
    else:
        pid = PIDController(0.7, 0.7, 0.00)
        velocity = pid.compute(difference)
        logger.info(f"Velocity by PID {velocity}")
        drone.send_rc_control(0, 0, -int(velocity), 0)
        logger.info(f"Sleep time {abs(difference) / velocity}")
        time.sleep(2.5)
        drone.send_rc_control(0, 0, 0, 0)


def hover_time(duration):
    """
    Hover the drone for the specified duration.

    Parameters:
    duration (int): The duration to hover in seconds.
    """
    loop_duration(duration)


def move_time(duration):
    """
    Move the drone for the specified duration.

    Parameters:
    duration (int): The duration to move in seconds.

    Process:
    1. Call loop_duration to manage the time-based loop.
    """
    loop_duration(duration)


def loop_duration(duration):
    """
    Execute a loop for the specified duration, logging each second.

    Parameters:
    duration (int): The total duration of the loop in seconds.

    Process:
    1. Log the start of the hover duration.
    2. Execute a loop that runs for the specified duration, decrementing the loop_time each second.
    3. Break the loop when the loop_time reaches zero.
    """
    logger.info(f"hovering for duration {duration}")
    loop_time = duration
    while True:
        sleep(1)
        loop_time = loop_time - 1
        if loop_time == 0:
            break


def attempt_2_routine(drone):
    """
    Perform a sequence of movements as part of the second attempt routine.

    Parameters:
    drone (Tello): Drone object to control movements.

    Process:
    1. Move the drone forward by 30 units and hover for 2 seconds.
    2. Move the drone right by 15 units and hover for 2 seconds.
    3. Move the drone left by 30 units and hover for 2 seconds.
    4. Move the drone right by 15 units and hover for 2 seconds.
    """
    drone.move_forward(30)
    hover_time(2)
    drone.move_right(15)
    hover_time(2)
    drone.move_left(30)
    hover_time(2)
    drone.move_right(15)
    hover_time(2)


def attempt_3_routine(drone):
    """
    Perform a sequence of movements as part of the third attempt routine.

    Parameters:
    drone (Tello): Drone object to control movements.

    Process:
    1. Move the drone back by 30 units and hover for 2 seconds.
    2. Move the drone up by 20 units and hover for 2 seconds.
    3. Rotate the drone clockwise by 15 degrees and hover for 2 seconds.
    4. Rotate the drone counter-clockwise by 30 degrees and hover for 2 seconds.
    5. Rotate the drone clockwise by 15 degrees and hover for 2 seconds.
    """
    drone.move_back(30)
    hover_time(2)
    drone.move_up(20)
    hover_time(2)
    drone.rotate_clockwise(15)
    hover_time(2)
    drone.rotate_counter_clockwise(30)
    hover_time(2)
    drone.rotate_clockwise(15)
    hover_time(2)

