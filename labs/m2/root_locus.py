"""Lab 2.4 (part 1) - Watch the closed-loop poles move as the gain increases."""
import control as ct
import matplotlib.pyplot as plt
import numpy as np

s = ct.tf("s")
plants = {
    "two poles:   50 / (s (0.2s+1))": 50 / (s * (0.2 * s + 1)),
    "three poles: 50 / (s (0.2s+1)(0.02s+1))": 50 / (s * (0.2 * s + 1) * (0.02 * s + 1)),
}
gains = np.logspace(-3, 0.5, 400)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, (name, G) in zip(axes, plants.items()):
    poles = np.array([np.sort_complex(ct.poles(ct.feedback(k * G, 1))) for k in gains])
    ax.plot(poles.real, poles.imag, ".", ms=2, color="tab:blue")
    open_loop = ct.poles(G)
    ax.plot(open_loop.real, open_loop.imag, "x", ms=10, mew=2, color="k", label="open-loop poles (gain 0)")
    ax.axvline(0, color="r", lw=1)
    ax.set_xlim(-60, 15)
    ax.set_ylim(-40, 40)
    ax.set_title(name)
    ax.set_xlabel("real part")
    ax.grid(True)
    ax.legend(loc="upper left")

    print(name)
    for k in (0.01, 0.025, 0.1, 0.5, 1.0, 1.2):
        p = ct.poles(ct.feedback(k * G, 1))
        worst = p[np.argmax(p.real)]
        verdict = "stable" if worst.real < 0 else "UNSTABLE"
        print(f"   kp = {k:5.3f}: rightmost pole {worst.real:7.2f}{worst.imag:+7.2f}j   {verdict}")
    unstable = [k for k, p in zip(gains, poles) if p.real.max() > 0]
    print("   stable for every gain tested" if not unstable else f"   becomes unstable near kp = {unstable[0]:.2f}")
axes[0].set_ylabel("imaginary part")
plt.tight_layout()
plt.show()
