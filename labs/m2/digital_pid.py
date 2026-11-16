"""Lab 2.7 - The same PID controller run at different sample rates.

Needs arm_sim.py and pid.py in the same folder.
"""
import control as ct
import matplotlib.pyplot as plt
import numpy as np

from arm_sim import simulate, step_metrics
from pid import PID

TARGET = np.deg2rad(90)
DURATION = 4.0

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 7))
print("control rate    period    overshoot   settling")
for rate in (1000, 100, 50, 20, 10, 5):
    dt = 1.0 / rate
    pid = PID(kp=20, ki=40, kd=2, dt=dt, u_min=-8, u_max=8)
    log = simulate(lambda t, theta: pid.update(TARGET, theta), DURATION, control_dt=dt)
    m = step_metrics(log["t"], log["theta"], TARGET)
    if np.isfinite(m["settle"]):
        print(f"  {rate:5d} Hz    {1000 * dt:5.1f} ms    {m['overshoot']:6.1f} %    {m['settle']:5.2f} s")
    else:
        print(f"  {rate:5d} Hz    {1000 * dt:5.1f} ms    does not settle: sustained oscillation")
    ax1.plot(log["t"], np.rad2deg(log["theta"]), label=f"{rate} Hz")
    if rate in (1000, 20, 10):
        ax2.plot(log["t"], log["u"], lw=0.8, label=f"{rate} Hz")

ax1.axhline(90, color="gray", lw=0.8)
ax1.set_ylim(0, 180)
ax1.set_ylabel("angle [deg]")
ax1.legend()
ax1.grid(True)
ax2.set_ylabel("motor torque [N m]")
ax2.set_xlabel("time [s]")
ax2.legend()
ax2.grid(True)

# --- Where do continuous poles go when you sample?  z = exp(s * T) ---
print("\npole of 1/(0.2 s + 1) at s = -5, sampled with a zero-order hold:")
G = ct.tf([1], [0.2, 1])
for T in (0.001, 0.02, 0.1):
    Gd = ct.sample_system(G, T, method="zoh")
    print(f"   T = {T:5.3f} s: discrete pole z = {ct.poles(Gd)[0].real:.4f}   (exp(-5 T) = {np.exp(-5 * T):.4f})")

plt.tight_layout()
plt.show()
