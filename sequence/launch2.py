import time

from djitellopy import Tello

drone = Tello()

previous_x: int = 0
previous_dir = "center"
desire_red_height: int = 140
desire_yellow_height: int = 90
set_timeout = 3000


def target_height(desire_height):
    resp = drone.send_command_with_return("height?", set_timeout)
    current_height = get_integers(resp)
    require_height = desire_height - (current_height * 10)
    print(f"current height : {current_height} required height :{require_height} desire height: {desire_height}")
    return require_height


def target(ring, dir):
    global previous_x
    global previous_dir

    # check drone is in center, else move it center
    if previous_x != 0:
        match previous_dir:
            case "left":
                print(f"checking condition in {previous_dir} with distance {previous_x}")
                # resp = drone.send_command_with_return(f"right {previous_x}", set_timeout)
                drone.move_right(previous_x)
                previous_x = 0
            case "right":
                print(f"checking condition in {previous_dir} with distance {previous_x}")
                # resp = resp = drone.send_command_with_return(f"left {previous_x}", set_timeout)
                drone.move_left(previous_x)
                previous_x = 0
            case "center":
                previous_x = 0
                pass
            case default:
                pass

    require_height = 0
    require_move = 0
    if ring == "red":
        require_height = target_height(desire_red_height)
    elif ring == "yellow":
        require_height = target_height(desire_yellow_height)

    if ring == "red":
        #drone.send_command_with_return(f"up {require_height}", set_timeout)
        drone.move_up(require_height)
        print(f"Red ring move up {require_height}")
        time.sleep(3)
        previous_dir = dir
    elif ring == "yellow":
        #drone.send_command_with_return(f"down {require_height}", set_timeout)
        drone.move_down(require_height)
        time.sleep(3)
        print(f"yellow ring move down {require_height}")
        #drone.send_command_with_return(f"{dir} {require_move}", set_timeout)
        if dir == "left":
            drone.move_left(require_move)
        elif dir == "right":
            drone.move_right(require_move)

        previous_dir = dir
        previous_x = require_move

    drone.send_command_with_return("forward 140", set_timeout)


def get_integers(values) -> int:
    numbers = []
    for char in values:
        if char.isdigit():
            numbers.append(int(char))
    return int(numbers[0])


def main():
    # flight take off
    drone.connect()
    drone.set_speed(20)
    drone.takeoff()

    seq = [
        ("red", "center"),
        ("yellow", "center"),
        ("red", "center")
    ]

    for s in seq:

        time.sleep(2)
        k = s[0]
        v = s[1]
        print(f"Inside Loop : {k} ring found with navigate to {v}")
        target(k, v)

        if 0xFF == ord('q'):
            drone.land()
            break

    # drone.land()


if __name__ == '__main__':
    main()
