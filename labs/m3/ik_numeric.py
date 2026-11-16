"""Lab 3.7 - Numerical inverse kinematics on a five-joint arm, tracing a circle.

Needs arms.py in the same folder.
"""
import matplotlib.pyplot as plt
import mujoco
import numpy as np

from arms import FIVE_DOF_XML, HOME, make, tip_pose

CENTER = np.array([0.20, 0.0, 0.12])
RADIUS = 0.06


def circle(n=120):
    """Points on a horizontal circle in front of the arm."""
    a = np.linspace(0, 2 * np.pi, n)
    return CENTER + RADIUS * np.stack([np.cos(a), np.sin(a), np.zeros_like(a)], axis=1)


def solve_ik(model, data, target, q0, method="dls", damping=0.05, tol=1e-4, max_iter=200,
             max_step=0.2, max_error=0.05):
    """Iterate q <- q + dq until the tip reaches `target`. Returns (q, iterations, final error)."""
    site = model.site("tip").id
    q = np.array(q0, float)
    jac = np.zeros((3, model.nv))
    for i in range(max_iter):
        pos, _ = tip_pose(model, data, q)
        error = target - pos
        distance = np.linalg.norm(error)
        if distance < tol:
            return q, i, distance
        if distance > max_error:                # far away: aim at a point max_error along the way
            error *= max_error / distance
        mujoco.mj_comPos(model, data)
        mujoco.mj_jacSite(model, data, jac, None, site)
        if method == "pinv":
            dq = np.linalg.pinv(jac) @ error
        elif method == "transpose":
            dq = 20.0 * jac.T @ error
        else:                                   # damped least squares
            dq = jac.T @ np.linalg.solve(jac @ jac.T + damping**2 * np.eye(3), error)
        step = np.abs(dq).max()
        if step > max_step:                     # keep each step inside the region where J is valid
            dq *= max_step / step
        q = np.clip(q + dq, model.jnt_range[:, 0], model.jnt_range[:, 1])
    return q, max_iter, np.linalg.norm(target - tip_pose(model, data, q)[0])


if __name__ == "__main__":
    np.set_printoptions(precision=3, suppress=True)
    model, data = make(FIVE_DOF_XML)
    print("home pose", HOME, "-> tip at", tip_pose(model, data, HOME)[0].round(3))

    # --- 1. One target, three methods ---
    target = np.array([0.22, 0.10, 0.15])
    print(f"\ntarget {target}")
    for method in ("transpose", "pinv", "dls"):
        q, n, err = solve_ik(model, data, target, HOME, method)
        print(f"  {method:9s}: {n:3d} iterations, error {1000 * err:.3f} mm, q = {q.round(3)}")

    # --- 2. A target that cannot be reached ---
    far = np.array([0.60, 0.0, 0.10])
    print(f"\nunreachable target {far}")
    for method in ("pinv", "dls"):
        q, n, err = solve_ik(model, data, far, HOME, method, max_iter=100)
        q_next, _, _ = solve_ik(model, data, far, q, method, max_iter=1)    # one more iteration
        print(f"  {method:5s}: stops {100 * err:.1f} cm short; joints still moving by "
              f"{np.rad2deg(np.abs(q_next - q).max()):.2f} deg per iteration")

    # --- 3. Trace the circle, starting each solve from the previous answer ---
    points = circle()
    q = np.array(HOME)
    qs, errors, iters = [], [], []
    for p in points:
        q, n, err = solve_ik(model, data, p, q)
        qs.append(q)
        errors.append(err)
        iters.append(n)
    qs = np.array(qs)
    traced = np.array([tip_pose(model, data, qi)[0] for qi in qs])
    print(f"\ncircle of {len(points)} points: largest error {1000 * max(errors):.3f} mm, "
          f"{np.mean(iters[1:]):.1f} iterations per point on average (first point: {iters[0]})")
    print("largest joint step between neighbouring points:",
          np.rad2deg(np.abs(np.diff(qs, axis=0)).max(axis=0)).round(2), "deg")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(points[:, 0], points[:, 1], "r--", label="commanded")
    ax1.plot(traced[:, 0], traced[:, 1], "b", lw=1, label="tip (MuJoCo)")
    ax1.set_aspect("equal")
    ax1.set_xlabel("x [m]")
    ax1.set_ylabel("y [m]")
    ax1.legend()
    ax1.grid(True)
    for j in range(model.njnt):
        ax2.plot(np.rad2deg(qs[:, j]), label=model.joint(j).name)
    ax2.set_xlabel("point on the circle")
    ax2.set_ylabel("joint angle [deg]")
    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()
    plt.show()
