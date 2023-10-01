from djitellopy import Tello

drone = Tello()
drone.connect()
print(drone.get_current_state())
drone.end()
