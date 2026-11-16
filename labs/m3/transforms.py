"""Lab 3.3 - Homogeneous transforms and chains of frames.

Scene: a robot base sits on a table. A camera is mounted above the table.
The camera sees a cube. Where is the cube relative to the robot base?
"""
import numpy as np
from scipy.spatial.transform import Rotation

np.set_printoptions(precision=3, suppress=True)


def transform(rotation, translation):
    """Build a 4x4 homogeneous transform from a 3x3 rotation and a translation."""
    T = np.eye(4)
    T[:3, :3] = rotation
    T[:3, 3] = translation
    return T


def inverse(T):
    """Inverse of a rigid transform, using R^T instead of a general matrix inverse."""
    R, p = T[:3, :3], T[:3, 3]
    return transform(R.T, -R.T @ p)


def apply(T, point):
    return (T @ np.append(point, 1.0))[:3]


def rot(axes, degrees):
    return Rotation.from_euler(axes, degrees, degrees=True).as_matrix()


# T_a_b means: the pose of frame b expressed in frame a. It maps points from b into a.
T_world_base = transform(rot("z", 90), [0.5, 0.2, 0.0])       # robot base on the table, turned 90 deg
T_world_cam = transform(rot("x", 180), [0.5, 0.6, 1.0])       # camera 1 m up, looking straight down
p_cam_cube = np.array([0.10, -0.05, 0.95])                    # the cube as the camera sees it

# Chain: base <- world <- camera
T_base_cam = inverse(T_world_base) @ T_world_cam
p_base_cube = apply(T_base_cam, p_cam_cube)
p_world_cube = apply(T_world_cam, p_cam_cube)

print("cube in camera frame:", p_cam_cube)
print("cube in world frame: ", p_world_cube)
print("cube in base frame:  ", p_base_cube)

# Check 1: going base -> world should give the same world point
print("\nround trip matches:", np.allclose(apply(T_world_base, p_base_cube), p_world_cube))

# Check 2: the fast inverse equals the general matrix inverse
print("fast inverse equals np.linalg.inv:", np.allclose(inverse(T_world_cam), np.linalg.inv(T_world_cam)))

# Check 3: order matters for transforms too
A = transform(rot("z", 90), [0, 0, 0])      # pure rotation
B = transform(np.eye(3), [1, 0, 0])         # pure translation along x
print("\nrotate then translate (B @ A) sends the origin to:", apply(B @ A, [0, 0, 0]))
print("translate then rotate (A @ B) sends the origin to:", apply(A @ B, [0, 0, 0]))

# A direction (not a point) ignores translation: use 0 as the fourth component
direction_cam = np.array([0.0, 0.0, 1.0])                     # the camera's viewing direction
print("\ncamera viewing direction in world frame:", (T_world_cam @ np.append(direction_cam, 0.0))[:3])
