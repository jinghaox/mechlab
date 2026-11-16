"""Lab 2.6 (part 3) - The derivative term amplifies sensor noise, and kicks on setpoint steps.

Needs arm_sim.py and pid.py in the same folder.
"""
import matplotlib.pyplot as plt
import numpy as np

from arm_sim import simulate
from pid import PID

TARGET = np.deg2rad(90)
NOISE = np.deg2rad(0.1)     # standard deviation of the angle measurement noise
DURATION = 4.0

CASES = {
    "no filter": dict(d_filter_tau=0.0),
    "filter 5 ms": dict(d_filter_tau=0.005),
    "filter 20 ms": dict(d_filter_tau=0.02),
    "filter 100 ms": dict(d_filter_tau=0.1),
}

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 7))
print(f"angle noise: {np.rad2deg(NOISE):.2f} deg RMS")
print("derivative       torque noise (RMS)   overshoot   angle jitter (RMS)")
for name, opts in CASES.items():
    pid = PID(kp=20, ki=40, kd=2, u_min=-8, u_max=8, **opts)
    log = simulate(lambda t, theta: pid.update(TARGET, theta), DURATION, noise_std=NOISE)
    tail = log["t"] > 3.0
    torque_noise = np.std(log["u_cmd"][tail])
    jitter = np.rad2deg(np.std(log["theta"][tail]))
    overshoot = max(log["theta"].max() / TARGET - 1, 0) * 100
    print(f"{name:14s}      {torque_noise:6.3f} N m        {overshoot:5.1f} %      {jitter:.4f} deg")
    ax1.plot(log["t"], np.rad2deg(log["theta"]), label=name)
    ax2.plot(log["t"], log["u_cmd"], lw=0.6, label=name)
ax1.set_ylabel("angle [deg]")
ax1.legend()
ax1.grid(True)
ax2.set_ylabel("commanded torque [N m]")
ax2.set_xlabel("time [s]")
ax2.grid(True)

# --- Derivative kick: differentiate the error, or only the measurement? ---
# The arm is already settled at 45 degrees when the setpoint jumps to 90.
START = np.deg2rad(45)
print("\nlargest torque command after a setpoint jump from 45 to 90 deg (no noise):")
for on_measurement in (False, True):
    pid = PID(kp=20, ki=40, kd=2, d_on_measurement=on_measurement)
    pid.update(START, START)      # one step at the old setpoint, so the derivative has a history
    log = simulate(lambda t, theta: pid.update(TARGET, theta), 0.5, theta0=START)
    which = "derivative of the measurement" if on_measurement else "derivative of the error      "
    print(f"   {which}: {np.max(np.abs(log['u_cmd'])):8.1f} N m")

plt.tight_layout()
plt.show()
