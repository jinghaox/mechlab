"""Lab 2.3 - Step-response specifications and two ways to tune a PID loop.

Plant: voltage -> angle of a motor with a slightly slow driver,
       G(s) = 50 / ( s (0.2 s + 1) (0.02 s + 1) )
"""
import control as ct
import matplotlib.pyplot as plt
import numpy as np

s = ct.tf("s")
G = 50 / (s * (0.2 * s + 1) * (0.02 * s + 1))
t = np.linspace(0, 3, 3001)


def pid_tf(kp, ki=0.0, kd=0.0, tau_d=0.005):
    """PID controller with a small filter on the derivative so it is realizable."""
    return kp + ki / s + kd * s / (tau_d * s + 1)


def report(name, C):
    closed = ct.feedback(C * G, 1)
    stable = np.all(ct.poles(closed).real < 0)
    if not stable:
        print(f"{name:34s} UNSTABLE")
        return None
    info = ct.step_info(closed, T=t)
    _, y = ct.step_response(closed, t)
    print(f"{name:34s} rise {info['RiseTime']:.3f} s   overshoot {info['Overshoot']:5.1f} %   "
          f"settling {info['SettlingTime']:.3f} s")
    return y


# --- Ziegler-Nichols: raise a pure P gain until the loop just oscillates ---
gm, pm, w_pc, w_gc = ct.margin(G)      # gm is the gain at which the loop becomes unstable
Ku, Tu = gm, 2 * np.pi / w_pc
print(f"ultimate gain Ku = {Ku:.3f}, oscillation period Tu = {Tu:.3f} s\n")

designs = {
    "P only, kp = 0.2": pid_tf(0.2),
    "P only, kp = 0.5": pid_tf(0.5),
    "P only, kp = 1.2 (above Ku)": pid_tf(1.2),
    "Ziegler-Nichols PID": pid_tf(0.6 * Ku, 1.2 * Ku / Tu, 0.075 * Ku * Tu),
    "hand-tuned PD, kp = 0.6, kd = 0.06": pid_tf(0.6, 0.0, 0.06),
}

for name, C in designs.items():
    y = report(name, C)
    if y is not None:
        plt.plot(t, y, label=name)

plt.axhline(1.0, color="gray", lw=0.8)
plt.xlabel("time [s]")
plt.ylabel("angle (reference = 1)")
plt.legend()
plt.grid(True)
plt.show()
