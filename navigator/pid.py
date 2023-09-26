class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, set_point, current_value):
        error = set_point - current_value
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp*error + self.ki*self.integral + self.kd*derivative
        self.prev_error = error
        return output
