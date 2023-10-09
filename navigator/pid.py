import time

from simple import PIDController, adjust_drone_position_y, adjust_drone_position_x
from drone_types import Direction


def adjust_height(drone, direction, height_difference):
    pid = PIDController(0.4, 0.4, 0.00)
    # Compute the velocity based on the height difference
    velocity_z = pid.compute(height_difference)

    if direction == Direction.UP:
        velocity_z = abs(velocity_z)
    elif direction == Direction.DOWN:
        velocity_z = -abs(velocity_z)

    print(f"Direction {direction} velocity {velocity_z}")

    max_velocity = 40
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
    # adjust_drone_position_y(drone,  20, Direction.UP,)
    direction = Direction.UP
    # adjust_drone_position_y(drone, 20, Direction.UP, )
    direction = Direction.LEFT
    adjust_drone_position_x(drone, 34, direction)
    direction = Direction.RIGHT
    adjust_drone_position_x(drone, 34, direction)


if __name__ == "__main__":
    main()
