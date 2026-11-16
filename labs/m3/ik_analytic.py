"""Lab 3.6 - Closed-form inverse kinematics of the two-link arm.

Needs arms.py in the same folder.
"""
import matplotlib.pyplot as plt
import numpy as np

from arms import L1, L2, TWO_LINK_XML, make, tip_pose


def ik(x, z, elbow_up=True):
    """Joint angles that put the tip at (x, z), or None if the point is out of reach."""
    r2 = x * x + z * z
    cos_q2 = (r2 - L1**2 - L2**2) / (2 * L1 * L2)          # law of cosines
    if abs(cos_q2) > 1:
        return None
    q2 = np.arccos(cos_q2)
    if elbow_up:
        q2 = -q2            # with z up, a negative elbow angle puts the elbow above the line to the target
    q1 = np.arctan2(z, x) - np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
    return np.array([q1, q2])


model, data = make(TWO_LINK_XML)

# --- 1. Two solutions for one target ---
target = np.array([0.35, 0.20])
print(f"target (x, z) = {target},  reach: {abs(L1 - L2):.2f} m to {L1 + L2:.2f} m")
for elbow_up in (True, False):
    q = ik(*target, elbow_up)
    tip, _ = tip_pose(model, data, q)
    print(f"  elbow {'up  ' if elbow_up else 'down'}: q = {np.rad2deg(q).round(2)} deg  ->  MuJoCo tip = {tip[[0, 2]].round(6)}")

# --- 2. Out of reach ---
for point in ((0.60, 0.10), (0.02, 0.01)):
    print(f"  target {point}: {'reachable' if ik(*point) is not None else 'no solution'}")

# --- 3. Follow a straight line and check the tip with MuJoCo ---
start, end = np.array([0.20, 0.30]), np.array([0.45, -0.10])
steps = 200
qs, errors = [], []
for s in np.linspace(0, 1, steps):
    p = (1 - s) * start + s * end
    q = ik(*p)
    tip, _ = tip_pose(model, data, q)
    qs.append(q)
    errors.append(np.linalg.norm(tip[[0, 2]] - p))
qs = np.rad2deg(np.array(qs))
print(f"\nstraight line from {start} to {end}: largest tip error {max(errors):.1e} m")
print(f"joint travel: shoulder {qs[:, 0].min():.1f} to {qs[:, 0].max():.1f} deg, elbow {qs[:, 1].min():.1f} to {qs[:, 1].max():.1f} deg")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
for i in range(0, steps, 25):
    q = np.deg2rad(qs[i])
    p1 = np.array([L1 * np.cos(q[0]), L1 * np.sin(q[0])])
    p2 = p1 + np.array([L2 * np.cos(q.sum()), L2 * np.sin(q.sum())])
    ax1.plot([0, p1[0], p2[0]], [0, p1[1], p2[1]], "o-", color="tab:blue", alpha=0.3 + 0.7 * i / steps)
ax1.plot([start[0], end[0]], [start[1], end[1]], "r--", label="commanded path")
ax1.set_aspect("equal")
ax1.set_xlabel("x [m]")
ax1.set_ylabel("z [m]")
ax1.legend()
ax1.grid(True)
ax2.plot(np.linspace(0, 1, steps), qs[:, 0], label="shoulder")
ax2.plot(np.linspace(0, 1, steps), qs[:, 1], label="elbow")
ax2.set_xlabel("fraction of the path")
ax2.set_ylabel("joint angle [deg]")
ax2.legend()
ax2.grid(True)
plt.tight_layout()
plt.show()
