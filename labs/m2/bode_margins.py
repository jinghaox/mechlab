"""Lab 2.5 - Bode plots, gain margin and phase margin."""
import control as ct
import matplotlib.pyplot as plt
import numpy as np

s = ct.tf("s")
G = 50 / (s * (0.2 * s + 1) * (0.02 * s + 1))
t = np.linspace(0, 4, 4001)
w = np.logspace(-1, 3, 500)


def margins(L):
    gm, pm, w_pc, w_gc = ct.margin(L)
    return 20 * np.log10(gm), pm, w_gc, w_pc


print("  kp     gain margin   phase margin   crossover    step overshoot")
for kp in (0.05, 0.1, 0.2, 0.5, 1.0):
    gm_db, pm, w_gc, w_pc = margins(kp * G)
    info = ct.step_info(ct.feedback(kp * G, 1), T=t)
    print(f" {kp:4.2f}    {gm_db:6.1f} dB      {pm:5.1f} deg     {w_gc:5.1f} rad/s    {info['Overshoot']:5.1f} %")

# --- The effect of a time delay (sensor lag, computation, communication) ---
kp = 0.2
print(f"\nwith kp = {kp}:")
for delay in (0.0, 0.01, 0.02, 0.05, 0.1):
    num, den = ct.pade(delay, 5)
    L = kp * G * ct.tf(num, den)
    gm_db, pm, w_gc, _ = margins(L)
    stable = np.all(ct.poles(ct.feedback(L, 1)).real < 0)
    print(f"   delay {1000 * delay:4.0f} ms: phase margin {pm:6.1f} deg   "
          f"(predicted loss {np.rad2deg(w_gc * delay):4.1f} deg)   {'stable' if stable else 'UNSTABLE'}")

# --- Bode plot of the loop for two gains ---
fig, (ax_mag, ax_phase) = plt.subplots(2, 1, sharex=True, figsize=(8, 7))
for kp in (0.1, 1.0):
    resp = ct.frequency_response(kp * G, w)
    mag_db = 20 * np.log10(np.abs(resp.fresp[0, 0]))
    phase = np.rad2deg(np.unwrap(np.angle(resp.fresp[0, 0])))
    ax_mag.semilogx(w, mag_db, label=f"kp = {kp}")
    ax_phase.semilogx(w, phase, label=f"kp = {kp}")
ax_mag.axhline(0, color="k", lw=0.8)
ax_mag.set_ylabel("magnitude [dB]")
ax_mag.legend()
ax_mag.grid(True, which="both")
ax_phase.axhline(-180, color="r", lw=0.8)
ax_phase.set_ylabel("phase [deg]")
ax_phase.set_xlabel("frequency [rad/s]")
ax_phase.grid(True, which="both")
plt.tight_layout()
plt.show()
