from djitellopy import Tello
from arch_logger import logger

def main():
    tello = Tello()

    try:
        tello.connect()
        battery_percentage = tello.get_battery()

        if int(battery_percentage) < 20:  # This is just an example, adjust according to your needs.
            logger.info("Battery is too low to fly.")
            return

        tello.takeoff()

        tello.move_left(100)
        tello.rotate_counter_clockwise(90)
        tello.move_forward(100)
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        logger.info("Force landing due to exception")
        tello.land()

if __name__ == "__main__":
    main()
