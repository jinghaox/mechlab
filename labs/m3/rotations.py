"""Lab 3.1 - Rotation matrices, the order of rotations, Euler angles and gimbal lock."""
import numpy as np
from scipy.spatial.transform import Rotation

np.set_printoptions(precision=3, suppress=True)


def Rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler_zyx(yaw, pitch, roll):
    """Yaw about z, then pitch about the new y, then roll about the new x."""
    return Rz(yaw) @ Ry(pitch) @ Rx(roll)


def to_euler_zyx(R):
    """Recover (yaw, pitch, roll) from a rotation matrix. Not unique when pitch = +/-90 deg."""
    pitch = -np.arcsin(R[2, 0])
    yaw = np.arctan2(R[1, 0], R[0, 0])
    roll = np.arctan2(R[2, 1], R[2, 2])
    return yaw, pitch, roll


d = np.deg2rad

# --- 1. What makes a matrix a rotation ---
R = Rz(d(30)) @ Ry(d(45))
print("R =\n", R)
print("R^T R = I ?", np.allclose(R.T @ R, np.eye(3)), "   det R =", round(np.linalg.det(R), 6))
print("columns of R are the rotated x, y, z axes; first column:", R[:, 0])

# --- 2. Order matters ---
A = Rz(d(90)) @ Rx(d(90))
B = Rx(d(90)) @ Rz(d(90))
v = np.array([1.0, 0.0, 0.0])
print("\nRz(90) Rx(90) applied to x:", A @ v)
print("Rx(90) Rz(90) applied to x:", B @ v)

# --- 3. Euler angles: there and back ---
angles = (d(40), d(25), d(-60))
R = euler_zyx(*angles)
print("\nyaw, pitch, roll in :", np.rad2deg(angles))
print("yaw, pitch, roll out:", np.rad2deg(to_euler_zyx(R)))
print("matches SciPy:", np.allclose(R, Rotation.from_euler("ZYX", angles).as_matrix()))

# --- 4. Gimbal lock: at pitch = 90 deg, yaw and roll do the same thing ---
R1 = euler_zyx(d(30), d(90), d(0))
R2 = euler_zyx(d(0), d(90), d(-30))
R3 = euler_zyx(d(50), d(90), d(20))
print("\npitch = 90 deg:")
print("(yaw 30, roll 0) equals (yaw 0, roll -30) ?", np.allclose(R1, R2))
print("(yaw 30, roll 0) equals (yaw 50, roll 20) ?", np.allclose(R1, R3))
print("only yaw - roll matters there: one degree of freedom has been lost")

# --- 5. Near gimbal lock, small rotations need huge angle changes ---
print("\nturn the body 1 deg about the world x axis, starting at different pitch angles:")
for pitch in (0, 60, 85, 89):
    before = euler_zyx(0, d(pitch), 0)
    after = Rx(d(1)) @ before
    yaw, _, roll = np.rad2deg(to_euler_zyx(after))
    print(f"   pitch {pitch:2d} deg: yaw changes by {yaw:7.2f} deg, roll by {roll:7.2f} deg")
