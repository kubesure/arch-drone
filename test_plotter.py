import plotter
from djitellopy import Tello

drone = Tello()
drone.connect()
drone.streamoff()
drone.streamon()
plotter.plot(True, True)
