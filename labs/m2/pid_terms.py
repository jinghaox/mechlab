"""Lab 2.2 - What P, I and D each do, on a one-joint arm in MuJoCo.

The arm starts hanging down and is commanded to 90 degrees (horizontal), where gravity
pulls hardest. Needs arm_sim.py and pid.py in the same folder.
"""
import matplotlib.pyplot as plt
import numpy as np

from arm_sim import TORQUE_LIMIT, arm_parameters, simulate, step_metrics
from pid import PID

TARGET = np.deg2rad(90)
DURATION = 8.0

inertia, gravity_torque, damping = arm_parameters()
print(f"arm: inertia = {inertia:.4f} kg m^2, gravity torque when horizontal = {gravity_torque:.2f} N m")

CASES = {
    "P    (kp=20)": dict(kp=20),
    "PD   (kp=20, kd=2)": dict(kp=20, kd=2),
    "PI   (kp=20, ki=40)": dict(kp=20, ki=40),
    "PID  (kp=20, ki=40, kd=2)": dict(kp=20, ki=40, kd=2),
}

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 7))
print("\ncontroller                   overshoot   settling    final error")
for name, gains in CASES.items():
    pid = PID(**gains, u_min=-TORQUE_LIMIT, u_max=TORQUE_LIMIT)   # the controller knows the motor's limit
    log = simulate(lambda t, theta: pid.update(TARGET, theta), DURATION)
    m = step_metrics(log["t"], log["theta"], TARGET)
    if m["overshoot"] > 150:
        print(f"{name:28s} unstable: the oscillation grows until the motor saturates")
    else:
        settle = f"{m['settle']:5.2f} s" if np.isfinite(m["settle"]) else "  never"
        print(f"{name:28s} {m['overshoot']:6.1f} %    {settle}    {np.rad2deg(m['final_error']):6.2f} deg")
    ax1.plot(log["t"], np.rad2deg(log["theta"]), label=name)
    ax2.plot(log["t"], log["u"], label=name)

ax1.axhline(90, color="gray", lw=0.8)
ax1.set_ylim(0, 180)
ax1.set_ylabel("angle [deg]")
ax1.legend()
ax1.grid(True)
ax2.set_ylabel("motor torque [N m]")
ax2.set_xlabel("time [s]")
ax2.grid(True)
plt.tight_layout()
plt.show()
