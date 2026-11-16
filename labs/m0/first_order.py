"""Lab 0.2 - Step response of an RC low-pass filter.

Simulates  tau * dy/dt + y = u  three ways and compares them:
  1. the exact solution           y(t) = 1 - exp(-t / tau)
  2. numerical integration        scipy.integrate.solve_ivp
  3. a transfer-function model    python-control
"""
import control as ct
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

R = 10e3      # ohms
C = 100e-6    # farads
tau = R * C   # time constant, seconds

t = np.linspace(0, 5 * tau, 500)


def rc(t, y):
    """Right-hand side dy/dt for a unit step input u = 1."""
    u = 1.0
    return (u - y) / tau


y_exact = 1 - np.exp(-t / tau)

sol = solve_ivp(rc, (t[0], t[-1]), y0=[0.0], t_eval=t, rtol=1e-8, atol=1e-10)
y_ivp = sol.y[0]

G = ct.tf([1], [tau, 1])          # G(s) = 1 / (tau*s + 1)
_, y_tf = ct.step_response(G, t)

print(f"time constant tau = {tau:.3f} s")
print(f"y(tau)            = {np.interp(tau, t, y_ivp):.4f}   (theory: {1 - np.exp(-1):.4f})")
print(f"max |solve_ivp - exact| = {np.max(np.abs(y_ivp - y_exact)):.2e}")
print(f"max |control   - exact| = {np.max(np.abs(y_tf - y_exact)):.2e}")

plt.plot(t, y_exact, label="exact")
plt.plot(t, y_ivp, "--", label="solve_ivp")
plt.plot(t, y_tf, ":", label="python-control")
plt.axvline(tau, color="gray", lw=0.8)
plt.axhline(1 - np.exp(-1), color="gray", lw=0.8)
plt.xlabel("time [s]")
plt.ylabel("capacitor voltage [V]")
plt.title("RC step response")
plt.legend()
plt.grid(True)
plt.show()
