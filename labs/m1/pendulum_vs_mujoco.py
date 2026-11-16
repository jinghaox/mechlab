"""Lab 1.3 (part 2) - Your own pendulum simulator against MuJoCo.

Needs pendulum_model.py from Lab 0.3 (in labs/m0, or copied next to this file).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import mujoco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "m0"))
from pendulum_model import GRAVITY, LENGTH, PENDULUM_XML  # noqa: E402

START_ANGLE_DEG = 60.0
DURATION = 10.0

model = mujoco.MjModel.from_xml_string(PENDULUM_XML)
data = mujoco.MjData(model)
h = model.opt.timestep

# --- Read the physical parameters MuJoCo computed from the geoms ---
body = model.body("pendulum").id
mass = model.body_mass[body]                    # rod + bob
d = np.linalg.norm(model.body_ipos[body])       # pivot to centre of mass
inertia_com = model.body_inertia[body][1]       # about the y axis, through the centre of mass
inertia_pivot = inertia_com + mass * d**2       # parallel-axis theorem

print(f"mass = {mass:.3f} kg, centre of mass at {d:.4f} m, inertia about pivot = {inertia_pivot:.5f} kg m^2")
print(f"point-mass idealisation would give             inertia about pivot = {1.0 * LENGTH**2:.5f} kg m^2")


def f(x, k):
    """Pendulum dynamics theta'' = -k * sin(theta)."""
    return np.array([x[1], -k * np.sin(x[0])])


def rk4_step(x, h, k):
    k1 = f(x, k)
    k2 = f(x + 0.5 * h * k1, k)
    k3 = f(x + 0.5 * h * k2, k)
    k4 = f(x + h * k3, k)
    return x + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


n = round(DURATION / h)
t = np.arange(n + 1) * h
x0 = np.array([np.deg2rad(START_ANGLE_DEG), 0.0])

# MuJoCo
data.qpos[0], data.qvel[0] = x0
theta_mj = np.zeros(n + 1)
for i in range(n + 1):
    theta_mj[i] = data.qpos[0]
    mujoco.mj_step(model, data)

# Your simulator, with two different models of the same pendulum
results = {}
for name, k in (("rigid body", mass * GRAVITY * d / inertia_pivot), ("point mass", GRAVITY / LENGTH)):
    x = x0.copy()
    theta = np.zeros(n + 1)
    for i in range(n + 1):
        theta[i] = x[0]
        x = rk4_step(x, h, k)
    results[name] = theta
    print(f"{name:10s} model: max difference from MuJoCo over {DURATION:.0f} s = {np.rad2deg(np.max(np.abs(theta - theta_mj))):.2e} deg")

plt.plot(t, np.rad2deg(theta_mj), label="MuJoCo")
plt.plot(t, np.rad2deg(results["rigid body"]), "--", label="my RK4, rigid body")
plt.plot(t, np.rad2deg(results["point mass"]), ":", label="my RK4, point mass")
plt.xlabel("time [s]")
plt.ylabel("angle [deg]")
plt.legend()
plt.grid(True)
plt.show()
