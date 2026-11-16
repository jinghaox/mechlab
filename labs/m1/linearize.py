"""Lab 1.6 - Linearize a pendulum and find out how far the linear model can be trusted."""
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

G, L, M = 9.81, 0.5, 1.0
DAMPING = 0.1    # viscous damping, as an angular-acceleration coefficient [1/s]


def f(x, u):
    """Nonlinear pendulum. x = [theta, omega], theta = 0 hanging down. u = torque [N m]."""
    theta, omega = x
    return np.array([omega, -(G / L) * np.sin(theta) - DAMPING * omega + u / (M * L**2)])


def jacobians(f, x0, u0, eps=1e-6):
    """A = df/dx and B = df/du at (x0, u0), by central differences."""
    n = len(x0)
    A = np.zeros((n, n))
    for i in range(n):
        dx = np.zeros(n)
        dx[i] = eps
        A[:, i] = (f(x0 + dx, u0) - f(x0 - dx, u0)) / (2 * eps)
    B = ((f(x0, u0 + eps) - f(x0, u0 - eps)) / (2 * eps)).reshape(n, 1)
    return A, B


np.set_printoptions(precision=3, suppress=True)
for name, theta0 in (("hanging down", 0.0), ("balanced upright", np.pi)):
    x_eq = np.array([theta0, 0.0])
    print(f"\n{name}:  f(x_eq, 0) = {f(x_eq, 0.0)}")
    A, B = jacobians(f, x_eq, 0.0)
    print("A =\n", A)
    print("B =", B.ravel())
    print("eigenvalues of A:", np.linalg.eigvals(A))

# --- Compare the nonlinear model with the linear one around "hanging down" ---
A, B = jacobians(f, np.zeros(2), 0.0)
t = np.linspace(0, 5, 2001)
fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True)
print("\nstart angle   max error of the linear model over 5 s")
for ax, deg in zip(axes, (5, 30, 90)):
    x0 = [np.deg2rad(deg), 0.0]
    nonlin = solve_ivp(lambda t, x: f(x, 0.0), (0, 5), x0, t_eval=t, rtol=1e-9, atol=1e-12).y[0]
    lin = solve_ivp(lambda t, x: A @ x, (0, 5), x0, t_eval=t, rtol=1e-9, atol=1e-12).y[0]
    err = np.rad2deg(np.max(np.abs(nonlin - lin)))
    print(f"   {deg:3d} deg     {err:6.2f} deg  ({100 * err / deg:.0f} % of the start angle)")
    ax.plot(t, np.rad2deg(nonlin), label="nonlinear")
    ax.plot(t, np.rad2deg(lin), "--", label="linearized")
    ax.set_title(f"released from {deg} deg")
    ax.set_xlabel("time [s]")
    ax.grid(True)
axes[0].set_ylabel("angle [deg]")
axes[0].legend()
plt.tight_layout()
plt.show()
