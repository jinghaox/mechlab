"""Lab 2.4 (part 2) - Stabilize the arm pointing straight up: an unstable plant made stable by feedback.

Needs arm_sim.py and pid.py in the same folder.
"""
import matplotlib.pyplot as plt
import numpy as np

from arm_sim import arm_parameters, simulate
from pid import PID

UPRIGHT = np.pi
START = np.pi - np.deg2rad(5)       # released 5 degrees away from vertical

inertia, gravity_torque, damping = arm_parameters()
print(f"inertia I = {inertia:.4f}, gravity torque m*g*d = {gravity_torque:.3f}, damping b = {damping}")

# Linearized about upright:  I * dd = +mgd * d - b * d' + u   (d = angle from vertical)
print(f"open-loop poles:   {np.roots([inertia, damping, -gravity_torque])}")
print("with PD feedback:  I s^2 + (b + kd) s + (kp - mgd) = 0\n")

fig, ax = plt.subplots(figsize=(8, 4.5))
for kp, kd in ((0.0, 0.0), (2.0, 0.5), (4.0, 0.0), (4.0, 0.5), (20.0, 2.0)):
    poles = np.roots([inertia, damping + kd, kp - gravity_torque])
    pid = PID(kp=kp, kd=kd)
    log = simulate(lambda t, theta: pid.update(UPRIGHT, theta), 4.0, theta0=START)
    off = np.rad2deg(np.abs(log["theta"] - UPRIGHT))
    result = "balances" if off.max() < 45 else "falls"
    print(f"kp = {kp:4.1f}, kd = {kd:3.1f}: poles {np.round(poles, 2)}  ->  {result}"
          f" (final offset {off[-1]:.2f} deg)")
    ax.plot(log["t"], np.rad2deg(log["theta"]), label=f"kp={kp}, kd={kd}")

ax.axhline(180, color="gray", lw=0.8)
ax.set_ylim(90, 270)
ax.set_xlabel("time [s]")
ax.set_ylabel("angle [deg]  (180 = upright)")
ax.legend()
ax.grid(True)
plt.show()
