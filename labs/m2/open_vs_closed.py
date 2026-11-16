"""Lab 2.1 - Open-loop against closed-loop speed control of the motor from Lab 1.1.

Plant:  J * dw/dt = K * u - b * w - load
The controller was designed for the nominal plant. We then test it on a plant whose
friction is 50 % higher, and hit it with a load torque at t = 2 s.
"""
import matplotlib.pyplot as plt
import numpy as np

J, B_NOMINAL, K = 2e-4, 1e-3, 0.05
TARGET = 100.0        # rad/s
LOAD = 0.02           # N m, applied from t = 2 s
DT = 1e-4


def run(controller, b):
    t = np.arange(0, 4, DT)
    w = np.zeros_like(t)
    integral = 0.0
    for i in range(len(t) - 1):
        error = TARGET - w[i]
        integral += error * DT
        u = controller(error, integral)
        load = LOAD if t[i] >= 2.0 else 0.0
        w[i + 1] = w[i] + DT * (K * u - b * w[i] - load) / J
    return t, w


KP, KI = 0.2, 4.0
controllers = {
    "open loop": lambda e, i: TARGET * B_NOMINAL / K,   # the voltage that gives TARGET on the nominal plant
    "P": lambda e, i: KP * e,
    "PI": lambda e, i: KP * e + KI * i,
}

fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
print(f"target = {TARGET:.0f} rad/s")
print("                 nominal plant               friction +50 %")
print("            before load   with load     before load   with load")
for name, ctrl in controllers.items():
    row = f"{name:10s}"
    for ax, b in zip(axes, (B_NOMINAL, 1.5 * B_NOMINAL)):
        t, w = run(ctrl, b)
        before, after = w[t < 2.0][-1], w[-1]
        row += f"   {before:7.1f}     {after:7.1f}     "
        ax.plot(t, w, label=name)
    print(row)

for ax, title in zip(axes, ("nominal plant", "friction +50 %")):
    ax.axhline(TARGET, color="gray", lw=0.8)
    ax.set_title(title)
    ax.set_xlabel("time [s]")
    ax.grid(True)
axes[0].set_ylabel("speed [rad/s]")
axes[0].legend()
plt.tight_layout()
plt.show()
