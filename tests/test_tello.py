from djitellopy import Tello
from navigator import common
import time
from drone_types import Direction

drone = Tello()


def rc_command(direction: Direction, speed):
    if direction.RIGHT:
        print(f"speed {speed} direction {direction}")
        drone.send_rc_control(speed, 0, 0, 0)
    elif direction.LEFT:
        print(f"speed {-abs(20)} direction {direction}")
        drone.send_rc_control(-abs(20), 0, 0, 0)
    elif direction.FORWARD:
        drone.send_rc_control(0, speed, 0, 0)
    elif direction.UP:
        speed = -speed
        drone.send_rc_control(0, 0, speed, 0)
    elif direction.DOWN:
        drone.send_rc_control(0, 0, speed, 0)
    elif direction.STOP:
        drone.send_command_with_return("stop")
        # drone.send_rc_control(0, 0, 0, 0)


try:
    drone.connect()
    print(drone.get_current_state())
    drone.takeoff()
    flight_duration = 20
    start_time = time.time()

    # while int(time.time() - start_time) < flight_duration:
    while True:
        common.hover_time(2)
        rc_command(Direction.RIGHT, 30)
        rc_command(Direction.STOP, 0)
        common.hover_time(3)
        rc_command(Direction.LEFT, 20)
        rc_command(Direction.STOP, 0)
        common.hover_time(3)
        break
    drone.end()
except KeyboardInterrupt:
    print("Ctrl+C pressed or process killed. Signalling main thread to land drone in emergency")
    drone.emergency()
except Exception as e:
    print(f"An error occurred: {str(e)}")
    drone.end()



