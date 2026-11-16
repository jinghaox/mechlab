"""Lab 0.3 - Watch the pendulum in MuJoCo's interactive viewer.

Run:  python pendulum_view.py
Close the window to stop. Double-click the bob, then Ctrl + right-drag to pull on it.
"""
import time

import mujoco
import mujoco.viewer
import numpy as np

from pendulum_model import PENDULUM_XML

model = mujoco.MjModel.from_xml_string(PENDULUM_XML)
data = mujoco.MjData(model)
data.qpos[0] = np.deg2rad(60)

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        step_start = time.time()
        mujoco.mj_step(model, data)
        viewer.sync()
        # Sleep so that simulated time advances at the same rate as real time.
        spare = model.opt.timestep - (time.time() - step_start)
        if spare > 0:
            time.sleep(spare)
