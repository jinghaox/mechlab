"""Lab 2.6 (part 2) - Integrator windup and how anti-windup fixes it.

The motor is limited to a torque only slightly larger than gravity, so a big move
saturates it for a long time. Needs arm_sim.py and pid.py in the same folder.
"""
import matplotlib.pyplot as plt
import numpy as np

from arm_sim import simulate, step_metrics
from pid import PID

TARGET = np.deg2rad(90)
LIMIT = 3.5        # N m. Gravity needs 2.94 N m at 90 degrees, so little is left to accelerate.
DURATION = 8.0

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(8, 9))
print("anti-windup   overshoot   settling   largest integral term")
for anti_windup in (False, True):
    pid = PID(kp=20, ki=40, kd=2, u_min=-LIMIT, u_max=LIMIT, anti_windup=anti_windup)
    integral_term = []

    def controller(t, theta):
        u = pid.update(TARGET, theta)
        integral_term.append(pid.ki * pid.integral)
        return u

    log = simulate(controller, DURATION)
    m = step_metrics(log["t"], log["theta"], TARGET)
    print(f"   {'on ' if anti_windup else 'off'}        {m['overshoot']:6.1f} %    {m['settle']:5.2f} s    {max(integral_term):6.1f} N m")
    label = f"anti-windup {'on' if anti_windup else 'off'}"
    ax1.plot(log["t"], np.rad2deg(log["theta"]), label=label)
    ax2.plot(log["t"], log["u"], label=label)
    ax3.plot(log["t"], integral_term, label=label)

ax1.axhline(90, color="gray", lw=0.8)
ax1.set_ylabel("angle [deg]")
ax1.legend()
ax2.set_ylabel("motor torque [N m]")
ax3.set_ylabel("integral term ki * I [N m]")
ax3.axhline(LIMIT, color="r", lw=0.8)
ax3.set_xlabel("time [s]")
for ax in (ax1, ax2, ax3):
    ax.grid(True)
plt.tight_layout()
plt.show()
