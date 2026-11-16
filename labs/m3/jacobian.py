"""Lab 3.5 - The Jacobian of the two-link arm: velocities, forces and singularities.

Needs arms.py in the same folder.
"""
import matplotlib.pyplot as plt
import mujoco
import numpy as np

from arms import L1, L2, TWO_LINK_XML, make, tip_pose

np.set_printoptions(precision=4, suppress=True)


def fk(q):
    return np.array([L1 * np.cos(q[0]) + L2 * np.cos(q[0] + q[1]),
                     L1 * np.sin(q[0]) + L2 * np.sin(q[0] + q[1])])


def jacobian(q):
    """Analytic Jacobian: rows are (x, z) of the tip, columns are the two joints."""
    s1, c1 = np.sin(q[0]), np.cos(q[0])
    s12, c12 = np.sin(q[0] + q[1]), np.cos(q[0] + q[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12],
                     [L1 * c1 + L2 * c12, L2 * c12]])


def jacobian_numeric(q, eps=1e-6):
    J = np.zeros((2, 2))
    for j in range(2):
        dq = np.zeros(2)
        dq[j] = eps
        J[:, j] = (fk(q + dq) - fk(q - dq)) / (2 * eps)
    return J


model, data = make(TWO_LINK_XML)
site = model.site("tip").id
q = np.deg2rad([40.0, 65.0])

# --- 1. Three ways to get the same Jacobian ---
tip_pose(model, data, q)
mujoco.mj_comPos(model, data)
jacp = np.zeros((3, model.nv))
mujoco.mj_jacSite(model, data, jacp, None, site)
print("analytic:\n", jacobian(q))
print("finite differences:\n", jacobian_numeric(q))
print("MuJoCo mj_jacSite (x and z rows):\n", jacp[[0, 2]])

# --- 2. Joint velocity -> tip velocity ---
qdot = np.array([1.0, -0.5])
print("\njoint velocity", qdot, "rad/s gives tip velocity", jacobian(q) @ qdot, "m/s")

# --- 3. Tip force -> joint torque:  tau = J^T F ---
force = np.array([0.0, -10.0])                      # 10 N pushing down on the tip
print("holding a 10 N downward load at the tip needs joint torques", -jacobian(q).T @ force, "N m")

# --- 4. Singularities: where det J = L1 * L2 * sin(q2) goes to zero ---
print("\n elbow angle    det J      L1*L2*sin(q2)   joint speed needed for 0.1 m/s outward")
for elbow in (90, 45, 10, 2, 0.5):
    q = np.deg2rad([20.0, elbow])
    J = jacobian(q)
    outward = fk(q) / np.linalg.norm(fk(q))         # direction straight away from the shoulder
    qdot = np.linalg.solve(J, 0.1 * outward)
    print(f"   {elbow:5.1f} deg   {np.linalg.det(J):8.5f}     {L1 * L2 * np.sin(q[1]):8.5f}"
          f"      {np.rad2deg(np.abs(qdot).max()):8.1f} deg/s")

# --- 5. Manipulability ellipses: tip velocities reachable with unit joint speed ---
fig, ax = plt.subplots(figsize=(7, 6))
circle = np.array([[np.cos(a), np.sin(a)] for a in np.linspace(0, 2 * np.pi, 100)]).T
for elbow in (120, 90, 45, 10):
    q = np.deg2rad([30.0, elbow])
    p1 = np.array([L1 * np.cos(q[0]), L1 * np.sin(q[0])])
    p2 = fk(q)
    ax.plot([0, p1[0], p2[0]], [0, p1[1], p2[1]], "o-", lw=3, label=f"elbow {elbow} deg")
    ellipse = jacobian(q) @ circle * 0.25           # scaled down for the picture
    ax.plot(p2[0] + ellipse[0], p2[1] + ellipse[1], "k", lw=1)
ax.set_aspect("equal")
ax.set_xlabel("x [m]")
ax.set_ylabel("z [m]")
ax.set_title("Manipulability ellipses of the two-link arm")
ax.legend()
ax.grid(True)
plt.show()
