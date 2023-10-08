import time
from djitellopy import Tello

import constants
import plotter
import utils
from drone_types import NavigatorInput, Ring, RingColor


class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, set_point, current_value):
        error = set_point - current_value
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output


def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello):
    forward_speed = constants.speed

    pid_x = PIDController(0, 0, 1)
    pid_y = PIDController(0, 0, 1)

    while True:
        # get current x y from detection
        current_ring = ring
        rings = plotter.plot(inn, utils.Cv2CapReaderWriter())
        new_ring = utils.get_avg_distance(rings)

        set_point_x = current_ring.x
        set_point_y = current_ring.y

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
    return True
