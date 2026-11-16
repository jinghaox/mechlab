"""Lab 3.2 - Quaternions and axis-angle: multiply, rotate, interpolate."""
import mujoco
import numpy as np
from scipy.spatial.transform import Rotation, Slerp

np.set_printoptions(precision=4, suppress=True)


def from_axis_angle(axis, angle):
    """Unit quaternion [w, x, y, z] for a rotation of `angle` about `axis`."""
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    return np.concatenate([[np.cos(angle / 2)], np.sin(angle / 2) * axis])


def multiply(p, q):
    """Quaternion product p * q: apply q first, then p."""
    pw, pv = p[0], p[1:]
    qw, qv = q[0], q[1:]
    return np.concatenate([[pw * qw - pv @ qv], pw * qv + qw * pv + np.cross(pv, qv)])


def conjugate(q):
    return np.concatenate([[q[0]], -q[1:]])


def rotate(q, v):
    """Rotate vector v by unit quaternion q:  q * (0, v) * q_conjugate."""
    return multiply(multiply(q, np.concatenate([[0.0], v])), conjugate(q))[1:]


d = np.deg2rad

# --- 1. Axis-angle to quaternion, and rotating a vector ---
q = from_axis_angle([0, 0, 1], d(90))
print("90 deg about z:       q =", q)
print("rotates x to:         ", rotate(q, np.array([1.0, 0, 0])))

# --- 2. Composition is quaternion multiplication ---
qz, qx = from_axis_angle([0, 0, 1], d(90)), from_axis_angle([1, 0, 0], d(90))
q_total = multiply(qz, qx)                       # x rotation first, then z
R_total = Rotation.from_euler("z", 90, degrees=True) * Rotation.from_euler("x", 90, degrees=True)
print("\nqz * qx =", q_total)
print("same rotation as the matrix product:", np.allclose(rotate(q_total, [1.0, 2, 3]), R_total.apply([1.0, 2, 3])))

# --- 3. q and -q are the same rotation ---
print("\nq and -q rotate identically:", np.allclose(rotate(q, [1.0, 2, 3]), rotate(-q, [1.0, 2, 3])))

# --- 4. Convention trap: MuJoCo stores [w, x, y, z], SciPy stores [x, y, z, w] ---
q_mj = np.zeros(4)
mujoco.mju_axisAngle2Quat(q_mj, np.array([0.0, 0, 1]), d(90))
q_scipy = Rotation.from_euler("z", 90, degrees=True).as_quat()
print("\nMuJoCo  [w x y z]:", q_mj)
print("SciPy   [x y z w]:", q_scipy)

# --- 5. Interpolating between two orientations ---
start = Rotation.from_euler("ZYX", [0, 0, 0], degrees=True)
end = Rotation.from_euler("ZYX", [170, 80, 170], degrees=True)
total = np.rad2deg((start.inv() * end).magnitude())
print(f"\nangle between start and end orientation: {total:.1f} deg")

fractions = np.linspace(0, 1, 11)
slerp = Slerp([0, 1], Rotation.concatenate([start, end]))
print("fraction   slerp: angle turned    Euler interpolation: angle turned")
for f, r in zip(fractions, slerp(fractions)):
    euler = Rotation.from_euler("ZYX", f * np.array([170, 80, 170]), degrees=True)
    a_slerp = np.rad2deg((start.inv() * r).magnitude())
    a_euler = np.rad2deg((start.inv() * euler).magnitude())
    print(f"  {f:.1f}          {a_slerp:6.1f} deg                 {a_euler:6.1f} deg")
