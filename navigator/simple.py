from drone_types import Direction, RingColor, Ring
from djitellopy import Tello
from time import sleep


class SimpleDroneNavigator:
    def __init__(self, config):
        self.config = config
        self.drone = Tello()

    def navigate_to(self,ring_data: Ring):
        self.drone.move_forward(ring_data.z)

    def hover_at(self, ring: RingColor, direction: Direction):
        height = 0
        duration = 10

        if ring == RingColor.RED:
            height = self.config['yellow_optimum_hover_ht']
        elif ring == RingColor.YELLOW:
            height = self.config['red_optimum_hover_ht']

        if direction == Direction.UP:
            self.drone.move_up(height)
        elif direction == Direction.DOWN:
            self.drone.move_down(height)

        hover = True
        hover_time = duration
        while hover:
            sleep(1)
            hover_time = hover_time - 1
            if hover_time == 0:
                hover = False
        return Ring(x=40, y=50, z=350, color=ring, area=300)
    