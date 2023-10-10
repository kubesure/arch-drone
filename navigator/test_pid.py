from djitellopy import Tello

import constants
import pid
from drone_types import Direction
from navigator.common import hover_time

drone = Tello()

def test_x():
    hover_time(2)
    direction = Direction.LEFT
    pid.adjust_drone_position_x(drone, 50, direction)
    hover_time(2)
    direction = Direction.RIGHT
    pid.adjust_drone_position_x(drone, 50, direction)


def test_y():
    hover_time(1)
    # direction = Direction.UP
    # pid.adjust_drone_position_y(drone,17, direction)
    # hover_time(2)
    direction = Direction.DOWN
    pid.adjust_drone_position_y(drone, 10, direction)
    hover_time(2)
    # hover_time(1)
    # direction = Direction.DOWN
    # pid.adjust_drone_position_y(drone, 20, direction)


try:
    drone.connect()
    drone.takeoff()
    # test_x()
    test_y()
    drone.end()
except KeyboardInterrupt:
    print("Ctrl+C pressed or process killed. Signalling main thread to land drone in emergency")
    drone.end()
except Exception as e:
    print(f"An error occurred: {str(e)}")
    drone.end()



