"""Lab 3.7 - Watch the five-joint arm trace the circle in MuJoCo's viewer.

The IK solution is sent to the arm's position actuators, so this is a real simulation:
the joints are driven by motors and the tip lags slightly behind the command.
Needs arms.py and ik_numeric.py in the same folder. Close the window to stop.
"""
import time

import mujoco
import mujoco.viewer
import numpy as np

from arms import FIVE_DOF_XML, HOME, make
from ik_numeric import circle, solve_ik

SECONDS_PER_LAP = 6.0

model, data = make(FIVE_DOF_XML)
planner_model, planner_data = make(FIVE_DOF_XML)      # a second copy, used only for solving IK

points = circle(240)
q_path, q = [], np.array(HOME)
for p in points:
    q, _, _ = solve_ik(planner_model, planner_data, p, q)
    q_path.append(q)
q_path = np.array(q_path)

data.qpos[:] = q_path[0]
data.ctrl[:] = q_path[0]
mujoco.mj_forward(model, data)

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        step_start = time.time()
        lap = (data.time % SECONDS_PER_LAP) / SECONDS_PER_LAP
        data.ctrl[:] = q_path[int(lap * (len(q_path) - 1))]
        mujoco.mj_step(model, data)
        viewer.sync()
        spare = model.opt.timestep - (time.time() - step_start)
        if spare > 0:
            time.sleep(spare)
