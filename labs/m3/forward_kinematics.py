"""Lab 3.4 - Forward kinematics four ways, checked against MuJoCo.

Needs arms.py in the same folder.
"""
import mujoco
import numpy as np
from scipy.linalg import expm

from arms import FIVE_DOF_XML, L1, L2, TWO_LINK_XML, make, tip_pose

np.set_printoptions(precision=4, suppress=True)


# ---------- The planar two-link arm ----------

def fk_trig(q1, q2):
    """Tip position (x, z) straight from trigonometry."""
    return np.array([L1 * np.cos(q1) + L2 * np.cos(q1 + q2),
                     L1 * np.sin(q1) + L2 * np.sin(q1 + q2)])


def planar(theta, length):
    """Planar transform: rotate by theta, then move `length` along the new x axis."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, length * c],
                     [s, c, length * s],
                     [0, 0, 1]])


def fk_chain(q1, q2):
    """Tip position from a chain of transforms, one per link."""
    return (planar(q1, L1) @ planar(q2, L2))[:2, 2]


def fk_dh(q1, q2):
    """Tip position from a DH table: rows are (theta, d, a, alpha)."""
    T = np.eye(4)
    for theta, d, a, alpha in ((q1, 0, L1, 0), (q2, 0, L2, 0)):
        ct, st, ca, sa = np.cos(theta), np.sin(theta), np.cos(alpha), np.sin(alpha)
        T = T @ np.array([[ct, -st * ca, st * sa, a * ct],
                          [st, ct * ca, -ct * sa, a * st],
                          [0, sa, ca, d],
                          [0, 0, 0, 1]])
    return T[:2, 3]         # the DH frame's x-y plane is the arm's plane


model, data = make(TWO_LINK_XML)
q = np.deg2rad([40.0, 65.0])
tip, _ = tip_pose(model, data, q)
print("two-link arm, q = [40, 65] deg")
print("  trigonometry :", fk_trig(*q))
print("  frame chain  :", fk_chain(*q))
print("  DH table     :", fk_dh(*q))
print("  MuJoCo (x, z):", tip[[0, 2]])


# ---------- Product of exponentials, for any arm ----------

def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def screw_matrix(axis, point):
    """4x4 matrix of a revolute joint's screw axis: rotation about `axis` through `point`."""
    S = np.zeros((4, 4))
    S[:3, :3] = skew(axis)
    S[:3, 3] = -np.cross(axis, point)
    return S


def read_screws(model, data):
    """Joint axes and the tip pose at the zero configuration, read from the MuJoCo model."""
    data.qpos[:] = 0
    mujoco.mj_kinematics(model, data)
    mujoco.mj_comPos(model, data)
    screws = [screw_matrix(data.xaxis[j].copy(), data.xanchor[j].copy()) for j in range(model.njnt)]
    M = np.eye(4)
    site = model.site("tip").id
    M[:3, :3] = data.site_xmat[site].reshape(3, 3)
    M[:3, 3] = data.site_xpos[site]
    return screws, M


def fk_poe(screws, M, q):
    """T(q) = exp(S1 q1) exp(S2 q2) ... exp(Sn qn) M"""
    T = np.eye(4)
    for S, angle in zip(screws, q):
        T = T @ expm(S * angle)
    return T @ M


model, data = make(FIVE_DOF_XML)
screws, M = read_screws(model, data)
print("\nfive-joint arm: tip at the zero configuration:", M[:3, 3])

rng = np.random.default_rng(1)
worst = 0.0
for _ in range(200):
    q = rng.uniform(model.jnt_range[:, 0], model.jnt_range[:, 1])
    T = fk_poe(screws, M, q)
    pos, rot = tip_pose(model, data, q)
    worst = max(worst, np.abs(T[:3, 3] - pos).max(), np.abs(T[:3, :3] - rot).max())
print(f"product of exponentials against MuJoCo, 200 random poses: largest difference {worst:.1e}")

q = np.array([0.5, 0.6, 1.2, 0.8, 0.3])
print("example pose q =", q, "-> tip at", fk_poe(screws, M, q)[:3, 3])
