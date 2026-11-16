"""Lab 1.5 - The mass-spring-damper in state-space form."""
import control as ct
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

m, k = 1.0, 100.0
zeta = 0.2
c = 2 * zeta * np.sqrt(k * m)

# State x = [position, velocity], input u = force, output y = position
A = np.array([[0.0, 1.0],
              [-k / m, -c / m]])
B = np.array([[0.0],
              [1.0 / m]])
C = np.array([[1.0, 0.0]])
D = np.array([[0.0]])

print("eigenvalues of A:", np.linalg.eigvals(A))

sys_ss = ct.ss(A, B, C, D)
G = ct.tf(sys_ss)                       # convert to a transfer function
print("transfer function:", G)
print("poles of G:      ", ct.poles(G))

# --- Simulate x' = A x + B u directly, with a 100 N step force ---
t = np.linspace(0, 5, 5001)
force = 100.0


def f(t, x):
    return A @ x + B[:, 0] * force


sol = solve_ivp(f, (t[0], t[-1]), [0.0, 0.0], t_eval=t, rtol=1e-9, atol=1e-12)
position, velocity = sol.y

_, y_ct = ct.step_response(force * sys_ss, t)
print(f"max difference, my simulation vs python-control: {np.max(np.abs(position - y_ct)):.2e} m")
print(f"final position {position[-1]:.4f} m  (static deflection F/k = {force / k:.4f} m)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
ax1.plot(t, position, label="position [m]")
ax1.plot(t, velocity / 10, label="velocity / 10 [m/s]")
ax1.set_xlabel("time [s]")
ax1.legend()
ax1.grid(True)

ax2.plot(position, velocity)
ax2.plot(position[0], velocity[0], "go", label="start")
ax2.plot(position[-1], velocity[-1], "rs", label="end")
ax2.set_xlabel("position [m]")
ax2.set_ylabel("velocity [m/s]")
ax2.set_title("State trajectory (phase plane)")
ax2.legend()
ax2.grid(True)
plt.tight_layout()
plt.show()
