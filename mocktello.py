class MockTello:
    def __init__(self):
        self.connected = False
        self.battery = 100
        self.height = 0
        self.speed = 0
        self.flight_time = 0
        self.stream_on = False
        self.flying = False
        self.height = 0

    def connect(self):
        self.connected = True
        return "ok"

    def disconnect(self):
        self.connected = False
        return "ok"

    def takeoff(self):
        if self.connected:
            self.height = 50  # Just a mock height after takeoff
            return "ok"
        return "error"

    def land(self):
        if self.connected:
            self.height = 0
            return "ok"
        return "error"

    def move_up(self, d: int):
        if self.connected:
            self.height += d
            return "ok"
        return "error"

    def move_down(self, d: int):
        if self.connected:
            self.height -= d
            return "ok"
        return "error"

    def move_left(self, d: int):
        # For simplicity, not altering state, just returning "ok"
        if self.connected:
            return "ok"
        return "error"

    def move_right(self, d: int):
        if self.connected:
            return "ok"
        return "error"

    def move_forward(self, d: int):
        if self.connected:
            return "ok"
        return "error"

    def move_backward(self, d: int):
        if self.connected:
            return "ok"
        return "error"

    def rotate_counter_clockwise(self, d: int):
        if self.connected:
            return "ok"
        return "error"

    def rotate_clockwise(self, d: int):
        if self.connected:
            return "ok"
        return "error"

    def flip(self, direction: str):
        if self.connected:
            return "ok"
        return "error"

    def get_battery(self) -> int:
        return self.battery

    def get_speed(self) -> int:
        return self.speed

    def get_flight_time(self) -> int:
        return self.flight_time

    def streamon(self):
        if self.connected:
            self.stream_on = True
            return "ok"
        return "error"

    def streamoff(self):
        if self.connected and self.stream_on:
            self.stream_on = False
            return "ok"
        return "error"

    def end(self):
        if self.connected:
            self.connected = False
            self.stream_on = False
            return "ok"
        return "error"

    def get_height(self) -> int:
        return self.height

    def emergency(self):
        print("Emergency situation detected!")
        self.land()


# Usage
mock_drone = MockTello()
mock_drone.connect()
print(mock_drone.takeoff())
print(mock_drone.move_up(30))
print(mock_drone.get_battery())
