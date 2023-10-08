import time
from drone_types import Direction

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


def adjust_drone_position_x(drone, difference, direction):
    pid = PIDController(0.4, 0.4, 0.00)
    velocity = pid.compute(difference)

    velocity = max(min(20, velocity), -20)
    print(f"velocity {velocity}")

    if direction == Direction.LEFT:
        if velocity > 0:
            drone.send_rc_control(-int(velocity), 0, 0, 0)
            print(f"sleep time {abs(difference) / velocity}")
            time.sleep(abs(difference) / velocity)
            drone.send_rc_control(0, 0, 0, 0)
    else:
        if velocity > 0:
            drone.send_rc_control(int(velocity), 0, 0, 0)
            print(f"sleep time {abs(difference) / velocity}")
            time.sleep(abs(difference) / velocity)
            drone.send_rc_control(0, 0, 0, 0)


def adjust_drone_position_y(drone, difference, direction):
    pid = PIDController(0.4, 0.4, 0.00)
    velocity = pid.compute(difference)

    velocity = max(min(20, velocity), -20)
    print(f"velocity {velocity}")

    if direction == Direction.UP:
        if velocity > 0:
            drone.send_rc_control(0, 0, int(velocity), 0)
            print(f"sleep time {abs(difference) / velocity}")
            time.sleep(abs(difference) / velocity)
            drone.send_rc_control(0, 0, 0, 0)
    else:
        if velocity > 0:
            drone.send_rc_control(0, 0, -int(velocity), 0)
            print(f"sleep time {abs(difference) / velocity}")
            time.sleep(abs(difference) / velocity)
            drone.send_rc_control(0, 0, 0, 0)


def adjust_height(drone, direction, height_difference):
    pid = PIDController(0.4, 0.4, 0.00)
    # Compute the velocity based on the height difference
    velocity_z = pid.compute(height_difference)

    if direction == Direction.UP:
        velocity_z = abs(velocity_z)
    elif direction == Direction.DOWN:
        velocity_z = -abs(velocity_z)

    print(f"Direction {direction} velocity {velocity_z}")

    max_velocity = 20
    velocity_z = max(min(velocity_z, max_velocity), -max_velocity)
    drone.send_rc_control(0, 0, int(velocity_z), 0)
    move_time = abs(height_difference) / velocity_z
    time.sleep(move_time)
    drone.send_rc_control(0, 0, 0, 0)


class MockDrone:
    """ A mock drone class to simulate the `send_rc_control` method """
    def send_rc_control(self, x, y, z, yaw):
        print(f"Drone moving with velocities: X:{x}, Y:{y}, Z:{z}, Yaw:{yaw}")


def main():
    drone = MockDrone()
    difference = 15
    direction = Direction.UP
    adjust_drone_position_y(drone,  17, Direction.UP,)
    adjust_drone_position_y(drone, 17, Direction.DOWN, )
    #direction = Direction.LEFT
    #adjust_drone_position_x(drone, difference, direction)
    # direction = Direction.RIGHT
    # adjust_drone_position(drone, difference, direction)



if __name__ == "__main__":
    main()
