"""Lab 1.3 (part 1) - Write Euler and RK4 yourself and measure how their error shrinks.

System: an ideal pendulum,  theta'' = -(g / L) * sin(theta)
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

G, L = 9.81, 0.5
X0 = np.array([np.deg2rad(30.0), 0.0])   # [angle, angular velocity]
T_END = 2.0      # compare the methods at this time [s]


def f(x):
    theta, omega = x
    return np.array([omega, -(G / L) * np.sin(theta)])


def euler_step(x, h):
    return x + h * f(x)


def rk4_step(x, h):
    k1 = f(x)
    k2 = f(x + 0.5 * h * k1)
    k3 = f(x + 0.5 * h * k2)
    k4 = f(x + h * k3)
    return x + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(step, h, t_end=T_END):
    n = round(t_end / h)
    xs = np.zeros((n + 1, 2))
    xs[0] = X0
    for i in range(n):
        xs[i + 1] = step(xs[i], h)
    return np.linspace(0, t_end, n + 1), xs


def energy(xs):
    """Energy per unit of m*L^2: kinetic + potential."""
    return 0.5 * xs[:, 1] ** 2 - (G / L) * np.cos(xs[:, 0])


# A very accurate reference solution.
ref = solve_ivp(lambda t, x: f(x), (0, T_END), X0, method="DOP853", rtol=1e-13, atol=1e-14)
theta_ref = ref.y[0, -1]

steps = [0.04, 0.02, 0.01, 0.005, 0.0025]
errors = {"Euler": [], "RK4": []}
print("    h      Euler error [deg]   RK4 error [deg]")
for h in steps:
    for name, step in (("Euler", euler_step), ("RK4", rk4_step)):
        _, xs = simulate(step, h)
        errors[name].append(abs(np.rad2deg(xs[-1, 0] - theta_ref)))
    print(f" {h:6.4f}  {errors['Euler'][-1]:14.4f}   {errors['RK4'][-1]:16.2e}")

for name in errors:
    slope = np.polyfit(np.log(steps), np.log(errors[name]), 1)[0]
    print(f"{name}: error is proportional to h^{slope:.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
ax1.loglog(steps, errors["Euler"], "o-", label="Euler")
ax1.loglog(steps, errors["RK4"], "s-", label="RK4")
ax1.set_xlabel("step size h [s]")
ax1.set_ylabel(f"angle error at t = {T_END:.0f} s [deg]")
ax1.legend()
ax1.grid(True, which="both")

for name, step in (("Euler", euler_step), ("RK4", rk4_step)):
    ts, xs = simulate(step, 0.01, t_end=20.0)
    print(f"{name}, h = 0.01: energy changes by {100 * (energy(xs)[-1] - energy(xs)[0]) / abs(energy(xs)[0]):+.3g} % in 20 s, final swing {np.rad2deg(np.max(np.abs(xs[-200:, 0]))):.1f} deg")
    ax2.plot(ts, energy(xs) - energy(xs)[0], label=f"{name}, h = 0.01")
ax2.set_xlabel("time [s]")
ax2.set_ylabel("energy error")
ax2.legend()
ax2.grid(True)
plt.tight_layout()
plt.show()
