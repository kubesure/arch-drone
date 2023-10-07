from djitellopy import Tello
from navigator import common
import cv2
import utils
from arch_logger import logger

drone = Tello()

try:
    drone.connect()
    logger.info(drone.get_current_state())
    drone.takeoff()
    _, video_reader = utils.get_out_writer(False)

    while True:
        # hover before move
        _, frame = video_reader.get_frame()
        common.hover(2)
        # move forward
        drone.send_rc_control(0, 0, 0, 0)
        # create drift move left
        drone.send_rc_control(-20, 0, 0, 0)
        # hover and read rings
        common.hover(4)
        # correct drift move right
        drone.send_rc_control(20, 0, 0, 0)
        # create drift by moving up and left
        drone.send_rc_control(-30, 0, -40, 0)
        # correct drift by moving down and right
        drone.send_rc_control(30, 0, 40, 0)
        # cv2.imshow("frame", frame)
        # wait for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_reader.release()
    cv2.destroyAllWindows()
    drone.end()
except KeyboardInterrupt:
    logger.info("Ctrl+C pressed or process killed. Signalling main thread to land drone in emergency")
    drone.emergency()
except Exception as e:
    print(f"An error occurred: {str(e)}")
    drone.end()

