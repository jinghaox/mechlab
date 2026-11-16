"""A one-joint arm with a motor, used by the Module 2 labs.

The joint angle is 0 with the arm hanging straight down and pi/2 with it horizontal.
The motor command is a torque in N m, limited to +/- TORQUE_LIMIT.
"""
import mujoco
import numpy as np

TORQUE_LIMIT = 8.0

ARM_XML = f"""
<mujoco model="arm">
  <option timestep="0.001" gravity="0 0 -9.81" integrator="RK4"/>

  <worldbody>
    <light pos="0 -1 2"/>
    <geom name="floor" type="plane" size="1 1 0.1" pos="0 0 -0.7" rgba="0.9 0.9 0.9 1"/>
    <body name="arm" pos="0 0 0">
      <joint name="shoulder" type="hinge" axis="0 1 0" damping="0.2"/>
      <geom name="link" type="capsule" fromto="0 0 0  0 0 -0.4" size="0.02" mass="0.5"/>
      <geom name="load" type="sphere" pos="0 0 -0.4" size="0.04" mass="0.5"/>
    </body>
  </worldbody>

  <actuator>
    <motor name="motor" joint="shoulder" ctrllimited="true" ctrlrange="-{TORQUE_LIMIT} {TORQUE_LIMIT}"/>
  </actuator>
</mujoco>
"""


def make_arm():
    model = mujoco.MjModel.from_xml_string(ARM_XML)
    return model, mujoco.MjData(model)


def arm_parameters():
    """Inertia about the joint [kg m^2], gravity torque when horizontal [N m], joint damping."""
    model, _ = make_arm()
    body = model.body("arm").id
    mass = model.body_mass[body]
    d = np.linalg.norm(model.body_ipos[body])
    inertia = model.body_inertia[body][1] + mass * d**2
    return inertia, mass * 9.81 * d, model.dof_damping[0]


def simulate(controller, duration, theta0=0.0, omega0=0.0, control_dt=0.001, noise_std=0.0,
             disturbance=None, seed=0):
    """Run the arm under a controller and return the recorded signals.

    controller(t, theta_measured) -> torque command. It is called every control_dt seconds and
    its output is held constant in between, like a real digital controller.
    noise_std    standard deviation of the noise added to the angle measurement [rad]
    disturbance  optional function t -> extra torque applied to the joint [N m]
    """
    model, data = make_arm()
    rng = np.random.default_rng(seed)
    h = model.opt.timestep
    hold = max(1, round(control_dt / h))
    n = round(duration / h)

    data.qpos[0], data.qvel[0] = theta0, omega0
    mujoco.mj_forward(model, data)

    log = {k: np.zeros(n) for k in ("t", "theta", "omega", "u", "u_cmd")}
    u_cmd = 0.0
    for i in range(n):
        if i % hold == 0:
            measured = data.qpos[0] + rng.normal(0.0, noise_std)
            u_cmd = float(controller(data.time, measured))
        data.ctrl[0] = u_cmd                      # MuJoCo clips this to the ctrlrange
        data.qfrc_applied[0] = disturbance(data.time) if disturbance else 0.0
        log["t"][i], log["theta"][i], log["omega"][i] = data.time, data.qpos[0], data.qvel[0]
        log["u_cmd"][i] = u_cmd
        log["u"][i] = np.clip(u_cmd, -TORQUE_LIMIT, TORQUE_LIMIT)
        mujoco.mj_step(model, data)
    return log


def step_metrics(t, y, target, start=0.0, band=0.02):
    """Rise time (10-90 %), overshoot [%], settling time and final error of a step response."""
    span = target - start
    frac = (y - start) / span
    t10 = t[np.argmax(frac >= 0.1)]
    t90 = t[np.argmax(frac >= 0.9)] if np.any(frac >= 0.9) else np.nan
    outside = np.where(np.abs(frac - 1.0) > band)[0]
    settle = t[min(outside[-1] + 1, len(t) - 1)] if len(outside) else 0.0
    if len(outside) and outside[-1] == len(t) - 1:
        settle = np.nan                           # never settled within the run
    return {
        "rise": t90 - t10,
        "overshoot": max(frac.max() - 1.0, 0.0) * 100,
        "settle": settle,
        "final_error": target - y[-500:].mean(),
    }
