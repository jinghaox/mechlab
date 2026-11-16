"""Lab 1.1 - A motor's speed is a first-order system. Measure its time constant from data.

Model:  J * dw/dt = K * u - b * w
  w  shaft speed [rad/s]        u  applied voltage [V]
  J  rotor + load inertia       b  viscous friction       K  torque per volt
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

J = 2e-4     # kg m^2
b = 1e-3     # N m s / rad
K = 0.05     # N m / V

STEP_VOLTS = 6.0
STEP_TIME = 0.1   # the voltage switches on at this time [s]

tau = J / b       # time constant
gain = K / b      # steady-state speed per volt


def voltage(t):
    return STEP_VOLTS if t >= STEP_TIME else 0.0


def motor(t, w):
    return (K * voltage(t) - b * w) / J


t = np.linspace(0, 1.5, 1501)
sol = solve_ivp(motor, (t[0], t[-1]), y0=[0.0], t_eval=t, max_step=1e-3)
w_true = sol.y[0]

# What an encoder would give you: the true speed plus measurement noise.
rng = np.random.default_rng(0)
w_meas = w_true + rng.normal(0, 3.0, size=t.shape)

# --- Estimate gain and time constant from the "measured" data only ---
w_final = w_meas[t > t[-1] - 0.3].mean()            # average over the flat tail
gain_est = w_final / STEP_VOLTS
i63 = np.argmax(w_meas >= 0.632 * w_final)          # first sample above 63.2 %
tau_est = t[i63] - STEP_TIME

print(f"model:     tau = {tau:.3f} s   gain = {gain:.1f} rad/s per V   final speed = {gain * STEP_VOLTS:.0f} rad/s")
print(f"from data: tau = {tau_est:.3f} s   gain = {gain_est:.1f} rad/s per V   final speed = {w_final:.0f} rad/s")

plt.plot(t, w_meas, ".", ms=2, color="0.6", label="measured (noisy)")
plt.plot(t, w_true, label="model")
plt.axhline(0.632 * w_final, color="gray", lw=0.8)
plt.axvline(STEP_TIME + tau_est, color="gray", lw=0.8)
plt.xlabel("time [s]")
plt.ylabel("speed [rad/s]")
plt.title("Motor speed step response")
plt.legend()
plt.grid(True)
plt.show()
