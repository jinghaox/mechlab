"""Lab 2.8 - A cascaded position / velocity loop against a single PID loop.

Plant: a motor-driven axis,  J * dw/dt = u - b * w - load,  d(theta)/dt = w
The motor torque is limited, and the axis should never exceed a speed limit.
"""
import matplotlib.pyplot as plt
import numpy as np

J, B = 0.01, 0.01          # kg m^2, N m s/rad
TORQUE_LIMIT = 2.0         # N m
SPEED_LIMIT = 5.0          # rad/s
TARGET = 10.0              # rad
LOAD, LOAD_TIME = 0.5, 6.0  # a load torque of 0.5 N m appears at t = 6 s
DT = 1e-4                  # simulation and control step


def single_loop():
    """One PID from position error straight to torque."""
    kp, ki, kd = 4.0, 8.0, 0.4
    state = {"i": 0.0}

    def control(theta, w):
        e = TARGET - theta
        u = kp * e + ki * state["i"] - kd * w
        u_sat = np.clip(u, -TORQUE_LIMIT, TORQUE_LIMIT)
        if u == u_sat:
            state["i"] += e * DT
        return u_sat

    return control


def cascade():
    """Outer loop: position error -> speed command. Inner loop: speed error -> torque."""
    kp_pos = 10.0                 # 1/s
    kp_vel, ki_vel = 1.0, 20.0    # inner loop about 10x faster than the outer one
    state = {"i": 0.0}

    def control(theta, w):
        w_cmd = np.clip(kp_pos * (TARGET - theta), -SPEED_LIMIT, SPEED_LIMIT)
        e = w_cmd - w
        u = kp_vel * e + ki_vel * state["i"]
        u_sat = np.clip(u, -TORQUE_LIMIT, TORQUE_LIMIT)
        if u == u_sat:
            state["i"] += e * DT
        return u_sat

    return control


def run(control):
    t = np.arange(0, 9, DT)
    theta, w, u = np.zeros_like(t), np.zeros_like(t), np.zeros_like(t)
    for i in range(len(t) - 1):
        u[i] = control(theta[i], w[i])
        load = LOAD if t[i] >= LOAD_TIME else 0.0
        w[i + 1] = w[i] + DT * (u[i] - B * w[i] - load) / J
        theta[i + 1] = theta[i] + DT * w[i + 1]
    return t, theta, w, u


fig, axes = plt.subplots(3, 1, sharex=True, figsize=(8, 9))
print("                peak speed   overshoot   time to within 1 %   dip after load   recovery")
for name, make in (("single PID", single_loop), ("cascade", cascade)):
    t, theta, w, u = run(make())
    before = t < LOAD_TIME
    overshoot = max(theta[before].max() / TARGET - 1, 0) * 100
    outside = np.where(np.abs(theta[before] - TARGET) > 0.01 * TARGET)[0]
    arrive = t[outside[-1] + 1]
    after = ~before
    dip = np.max(np.abs(theta[after] - TARGET))
    late = np.where(np.abs(theta[after] - TARGET) > 0.1 * dip)[0]
    recover = t[after][late[-1]] - LOAD_TIME
    print(f"{name:12s}   {np.abs(w).max():6.2f} rad/s   {overshoot:5.1f} %        {arrive:5.2f} s"
          f"          {dip:6.3f} rad     {recover:5.2f} s")
    axes[0].plot(t, theta, label=name)
    axes[1].plot(t, w, label=name)
    axes[2].plot(t, u, label=name)

axes[0].axhline(TARGET, color="gray", lw=0.8)
axes[0].set_ylabel("position [rad]")
axes[0].legend()
axes[1].axhline(SPEED_LIMIT, color="r", lw=0.8)
axes[1].set_ylabel("speed [rad/s]")
axes[2].set_ylabel("torque [N m]")
axes[2].set_xlabel("time [s]")
for ax in axes:
    ax.grid(True)
plt.tight_layout()
plt.show()
