"""A discrete PID controller, used by the Module 2 labs.

Lesson 2.2 uses only kp, ki and kd. The other options are explained in lesson 2.6.
"""


class PID:
    def __init__(self, kp, ki=0.0, kd=0.0, dt=0.001, u_min=None, u_max=None,
                 anti_windup=True, d_filter_tau=0.0, d_on_measurement=True):
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.u_min, self.u_max = u_min, u_max
        self.anti_windup = anti_windup
        self.d_filter_tau = d_filter_tau            # time constant of the derivative low-pass [s]
        self.d_on_measurement = d_on_measurement    # differentiate -y instead of the error
        self.reset()

    def reset(self):
        self.integral = 0.0
        self.prev = None        # previous value of the differentiated signal
        self.d_term = 0.0       # filtered derivative

    def update(self, r, y, feedforward=0.0):
        """One control step. r = reference, y = measurement. Returns the command u."""
        error = r - y

        # Derivative: finite difference, then an optional first-order low-pass filter.
        signal = -y if self.d_on_measurement else error
        raw = 0.0 if self.prev is None else (signal - self.prev) / self.dt
        self.prev = signal
        alpha = self.dt / (self.d_filter_tau + self.dt)
        self.d_term += alpha * (raw - self.d_term)

        u_unsat = feedforward + self.kp * error + self.ki * self.integral + self.kd * self.d_term
        u = u_unsat
        if self.u_max is not None:
            u = min(u, self.u_max)
        if self.u_min is not None:
            u = max(u, self.u_min)

        # Integrate, unless the output is saturated and the error would push it further in.
        pushing_further = (u != u_unsat) and (error * (u_unsat - u) > 0)
        if not (self.anti_windup and pushing_further):
            self.integral += error * self.dt
        return u
