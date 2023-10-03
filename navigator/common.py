from time import sleep

from djitellopy import Tello

from drone_types import NavigatorInput, Direction, RingColor


def hover_at(inn: NavigatorInput, drone: Tello, attempt):
    print(f"attempt {attempt} on ring {inn.ring} with duration {inn.duration}")

    # TODO write exception handling since its a thread inform main thread

    y_direction, y_movement = get_optimum_hover_height(drone, inn)
    hover_to_y(drone, inn, y_direction, y_movement)

    if attempt == 1:
        print(f"attempt {attempt} executing scan")
        hover(inn.duration)
    elif attempt == 2:
        print(f"attempt {attempt} executing scan")
        attempt_2_routine(drone)
    elif attempt == 3:
        print(f"attempt {attempt} executing scan")
        attempt_3_routine(drone)


def get_optimum_hover_height(drone, inn):
    y_movement = 0
    y_direction = Direction.UP
    drone_height = drone.get_height()
    red_height = int(inn.config['red_optimum_hover_ht'])
    yellow_height = int(inn.config['yellow_optimum_hover_ht'])
    if inn.ring == RingColor.RED:
        print(f" red height {yellow_height} drone height {drone_height}")
        y_movement = red_height
        if drone_height > red_height:
            y_direction = Direction.DOWN
            y_movement = abs(drone_height - red_height)
        elif drone_height < red_height:
            y_direction = Direction.UP
            y_movement = abs(drone_height - red_height)
        print(f"y_direction {y_direction} y_movement {y_movement} ring {inn.ring}")
    elif inn.ring == RingColor.YELLOW:
        print(f" yellow height {yellow_height} drone height {drone_height}")
        y_movement = yellow_height
        if drone_height > yellow_height:
            y_direction = Direction.DOWN
            y_movement = abs(drone_height - yellow_height)
        elif drone_height < yellow_height:
            y_direction = Direction.UP
            y_movement = abs(drone_height - yellow_height)
        elif drone_height == yellow_height:
            y_direction = Direction.HOVER
        print(f"y_direction {y_direction} y_movement {y_movement} ring {inn.ring}")
    return y_direction, y_movement


def hover_to_y(drone, inn, y_direction, y_movement):
    if y_direction == Direction.UP:
        print(f"move up {y_movement} ring {inn.ring}")
        drone.move_up(y_movement)
    elif y_direction == Direction.DOWN:
        print(f"move down {y_movement} ring {inn.ring}")
        drone.move_down(y_movement)
    elif y_direction == Direction.HOVER:
        print(f"hovering at height {drone.get_height()}")


def hover(duration):
    print(f"hovering for duration {duration}")
    hover_time = duration
    while True:
        sleep(1)
        hover_time = hover_time - 1
        if hover_time == 0:
            break


def attempt_2_routine(drone):
    drone.move_forward(30)
    hover(2)
    drone.move_right(15)
    hover(2)
    drone.move_left(30)
    hover(2)
    drone.move_right(15)
    hover(2)


def attempt_3_routine(drone):
    drone.move_back(30)
    hover(2)
    drone.move_up(20)
    hover(2)
    drone.rotate_clockwise(15)
    hover(2)
    drone.rotate_counter_clockwise(30)
    hover(2)
    drone.rotate_clockwise(15)
    hover(2)
