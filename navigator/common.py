from time import sleep
from djitellopy import Tello
import time
import constants
from drone_types import NavigatorInput, Direction, RingColor
from arch_logger import logger


def hover_at(inn: NavigatorInput, drone: Tello, attempt):
    logger.debug(f"attempt {attempt} on ring {inn.ring_color} with duration {inn.duration}")

    # TODO write exception handling since its a thread inform main thread

    if attempt != 4:
        y_direction, y_movement = get_optimum_hover_height(drone, inn)
        move_to_y(drone, inn, y_direction, y_movement)

    if attempt == 1:
        logger.debug(f"attempt {attempt} executing scan")
        hover_time(inn.duration)
    elif attempt == 2:
        logger.debug(f"attempt {attempt} executing scan")
        attempt_2_routine(drone)
    elif attempt == 3:
        logger.debug(f"attempt {attempt} executing scan")
        attempt_3_routine(drone)


def get_optimum_hover_height(drone, inn):
    y_movement = 0
    y_direction = Direction.UP
    drone_height = drone.get_height()
    red_height = constants.red_optimum_hover_ht
    yellow_height = constants.yellow_optimum_hover_ht
    if inn.ring_color == RingColor.RED:
        logger.info(f" red height {red_height} drone height {drone_height}")
        y_movement = red_height
        if drone_height > red_height:
            y_direction = Direction.DOWN
            y_movement = abs(drone_height - red_height)
        elif drone_height < red_height:
            y_direction = Direction.UP
            y_movement = abs(drone_height - red_height)
        logger.debug(f"y_direction {y_direction} y_movement {y_movement} ring {inn.ring_color}")
    elif inn.ring_color == RingColor.YELLOW:
        logger.info(f" yellow height {yellow_height} drone height {drone_height}")
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
    threshold = constants.hover_up_down_threshold
    if y_direction == Direction.UP:
        logger.info(f"moving up {y_movement} ring {inn.ring_color}")
        if y_movement > threshold:
            # adjust_drone_position_y(drone, y_movement, y_direction)
            drone.move_up(y_movement)
    elif y_direction == Direction.DOWN:
        logger.info(f"moving down {y_movement} ring {inn.ring_color}")
        if y_movement > threshold:
            # adjust_drone_position_y(drone, y_movement, y_direction)
            drone.move_down(y_movement)
    elif y_direction == Direction.HOVER:
        logger.info(f"hovering at height {drone.get_height()}")


class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        # speed = pid[0] * error + pid[1] * (error - pError)
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output


def adjust_drone_position_z(drone, difference, direction):
    pid = PIDController(0.50, 0.50, 0.00)
    velocity = pid.compute(difference)
    logger.info(f"velocity from PID controller {velocity}")

    # velocity = constants.max_velocity_right_left
    logger.info(f"velocity {velocity}")

    if direction == Direction.FORWARD:
        logger.info(f"rc command {direction}")
        drone.send_rc_control(0, int(velocity), 0, 0)
        logger.info(f"sleep time {abs(difference) / velocity}")
        time.sleep(abs(difference) / velocity)
        drone.send_rc_control(0, 0, 0, 0)
    elif direction == Direction.BACKWARD:
        logger.info(f"rc command {direction}")
        drone.send_rc_control(-int(velocity), 0, 0, 0)
        logger.info(f"sleep time {abs(difference) / velocity}")
        time.sleep(abs(difference) / velocity)
        drone.send_rc_control(0, 0, 0, 0)


def adjust_drone_position_x(drone, difference, direction):
    pid = PIDController(0.50, 0.50, 0.00)
    velocity = pid.compute(difference)
    logger.info(f"velocity from PID controller {velocity}")

    # velocity = constants.max_velocity_right_left
    logger.info(f"velocity {velocity}")

    if direction == Direction.LEFT:
        logger.info(f"rc command {direction}")
        drone.send_rc_control(-int(velocity), 0, 0, 0)
        logger.info(f"sleep time {abs(difference) / velocity}")
        time.sleep(1.25)
        drone.send_rc_control(0, 0, 0, 0)
    else:
        logger.info(f"rc command {direction}")
        drone.send_rc_control(int(velocity), 0, 0, 0)
        logger.info(f"sleep time {abs(difference) / velocity}")
        time.sleep(1.25)
        drone.send_rc_control(0, 0, 0, 0)


def adjust_drone_position_y(drone, difference, direction):
    if direction == Direction.UP:
        pid = PIDController(0.7, 0.7, 0.00)
        velocity = pid.compute(difference)
        # velocity = max(min(constants.max_velocity_up_down, velocity), -constants.max_velocity_up_down)
        logger.info(f"velocity by pid {velocity}")
        drone.send_rc_control(0, 0, int(velocity), 0)
        logger.info(f"sleep time {abs(difference) / velocity}")
        # time.sleep(abs(difference) / velocity)
        time.sleep(2.5)
        drone.send_rc_control(0, 0, 0, 0)
    else:
        pid = PIDController(0.7, 0.7, 0.00)
        velocity = pid.compute(difference)
        # velocity = max(min(constants.max_velocity_up_down, velocity), -constants.max_velocity_up_down)
        logger.info(f"velocity by pid {velocity}")
        drone.send_rc_control(0, 0, -int(velocity), 0)
        logger.info(f"sleep time {abs(difference) / velocity}")
        time.sleep(2.5)
        # time.sleep(abs(difference) / velocity)
        drone.send_rc_control(0, 0, 0, 0)


def hover_time(duration):
    loop_duration(duration)


def move_time(duration):
    loop_duration(duration)


def loop_duration(duration):
    logger.info(f"hovering for duration {duration}")
    loop_time = duration
    while True:
        sleep(1)
        loop_time = loop_time - 1
        if loop_time == 0:
            break


def attempt_2_routine(drone):
    drone.move_forward(30)
    hover_time(2)
    drone.move_right(15)
    hover_time(2)
    drone.move_left(30)
    hover_time(2)
    drone.move_right(15)
    hover_time(2)


def attempt_3_routine(drone):
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
