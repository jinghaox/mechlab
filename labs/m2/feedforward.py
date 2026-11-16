"""Lab 2.6 (part 1) - Feedforward: tell the motor what you already know.

The arm follows a smooth back-and-forth motion between 0 and 90 degrees.
Needs arm_sim.py and pid.py in the same folder.
"""
import matplotlib.pyplot as plt
import numpy as np

from arm_sim import arm_parameters, simulate
from pid import PID

inertia, gravity_torque, damping = arm_parameters()
AMPLITUDE = np.deg2rad(45)
W = np.pi          # rad/s, one full back-and-forth every 2 s
DURATION = 6.0


def reference(t):
    """Angle, velocity and acceleration of the desired motion."""
    return (AMPLITUDE * (1 - np.cos(W * t)),
            AMPLITUDE * W * np.sin(W * t),
            AMPLITUDE * W**2 * np.cos(W * t))


def gravity_ff(t):
    r, _, _ = reference(t)
    return gravity_torque * np.sin(r)


def full_ff(t):
    r, r_vel, r_acc = reference(t)
    return inertia * r_acc + damping * r_vel + gravity_torque * np.sin(r)


# The reference is smooth, so the derivative acts on the error (see the lesson).
PD = dict(kp=20, kd=2, d_on_measurement=False, u_min=-8, u_max=8)
CASES = {
    "PD only": (PD, None),
    "PID": (dict(PD, ki=40), None),
    "PD + gravity feedforward": (PD, gravity_ff),
    "PD + full feedforward": (PD, full_ff),
    "PD on measurement + full ff": (dict(PD, d_on_measurement=True), full_ff),
}

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 7))
print("controller                    RMS error    max error")
for name, (gains, ff) in CASES.items():
    pid = PID(**gains)

    def controller(t, theta, pid=pid, ff=ff):
        return pid.update(reference(t)[0], theta, feedforward=ff(t) if ff else 0.0)

    log = simulate(controller, DURATION)
    err = np.rad2deg(reference(log["t"])[0] - log["theta"])
    steady = log["t"] > 2.0                       # ignore the start-up transient
    print(f"{name:28s} {np.sqrt(np.mean(err[steady] ** 2)):6.2f} deg   {np.max(np.abs(err[steady])):6.2f} deg")
    ax1.plot(log["t"], err, label=name)
    ax2.plot(log["t"], log["u"], label=name)

ax1.set_ylabel("tracking error [deg]")
ax1.legend()
ax1.grid(True)
ax2.set_ylabel("motor torque [N m]")
ax2.set_xlabel("time [s]")
ax2.grid(True)
plt.tight_layout()
plt.show()
