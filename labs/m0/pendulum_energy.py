"""Lab 0.3 - Swing a pendulum in MuJoCo and track its energy.

Run:  python pendulum_energy.py
"""
import matplotlib.pyplot as plt
import mujoco
import numpy as np

from pendulum_model import GRAVITY, LENGTH, PENDULUM_XML

START_ANGLE_DEG = 30.0
DURATION = 10.0   # seconds

model = mujoco.MjModel.from_xml_string(PENDULUM_XML)
data = mujoco.MjData(model)

# Ask MuJoCo to compute potential and kinetic energy at every step.
model.opt.enableflags |= mujoco.mjtEnableBit.mjENBL_ENERGY

# Initial condition: released from rest at START_ANGLE_DEG.
data.qpos[0] = np.deg2rad(START_ANGLE_DEG)
data.qvel[0] = 0.0
mujoco.mj_forward(model, data)   # compute everything that depends on qpos/qvel

n_steps = int(DURATION / model.opt.timestep)
t = np.zeros(n_steps)
angle = np.zeros(n_steps)
potential = np.zeros(n_steps)
kinetic = np.zeros(n_steps)

for i in range(n_steps):
    t[i] = data.time
    angle[i] = data.qpos[0]
    potential[i], kinetic[i] = data.energy
    mujoco.mj_step(model, data)

total = potential + kinetic

# Measure the period from upward zero crossings of the angle.
crossings = np.where((angle[:-1] < 0) & (angle[1:] >= 0))[0]
period = np.mean(np.diff(t[crossings])) if len(crossings) > 1 else float("nan")
small_angle_period = 2 * np.pi * np.sqrt(LENGTH / GRAVITY)

print(f"timestep            = {model.opt.timestep} s, {n_steps} steps")
print(f"measured period     = {period:.4f} s")
print(f"small-angle formula = {small_angle_period:.4f} s")
print(f"energy drift        = {total[-1] - total[0]:+.2e} J  (start {total[0]:.4f} J)")

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
ax1.plot(t, np.rad2deg(angle))
ax1.set_ylabel("angle [deg]")
ax1.grid(True)

ax2.plot(t, potential, label="potential")
ax2.plot(t, kinetic, label="kinetic")
ax2.plot(t, total, "k", label="total")
ax2.set_xlabel("time [s]")
ax2.set_ylabel("energy [J]")
ax2.legend()
ax2.grid(True)
plt.show()
