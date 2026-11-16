"""Arm models shared by the Module 3 labs.

TWO_LINK   a planar arm in the vertical x-z plane. Both joints turn about the -y axis, so a
           positive angle lifts the link from the +x direction toward +z.
FIVE_DOF   a small desktop arm with the joint layout of the SO-101: shoulder pan, shoulder
           lift, elbow flex, wrist flex, wrist roll. The geometry is simplified and the link
           lengths are approximate. At q = 0 it points straight up.
"""
import mujoco

L1, L2 = 0.30, 0.25            # two-link arm: link lengths [m]

TWO_LINK_XML = f"""
<mujoco model="two_link">
  <option timestep="0.001" gravity="0 0 -9.81" integrator="RK4"/>
  <worldbody>
    <light pos="0 -1 2"/>
    <body name="link1" pos="0 0 0">
      <joint name="shoulder" type="hinge" axis="0 -1 0" damping="0.1"/>
      <geom type="capsule" fromto="0 0 0  {L1} 0 0" size="0.02" mass="1.0" rgba="0.2 0.5 0.8 1"/>
      <body name="link2" pos="{L1} 0 0">
        <joint name="elbow" type="hinge" axis="0 -1 0" damping="0.1"/>
        <geom type="capsule" fromto="0 0 0  {L2} 0 0" size="0.018" mass="0.6" rgba="0.9 0.5 0.2 1"/>
        <site name="tip" pos="{L2} 0 0" size="0.015" rgba="1 0 0 1"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="shoulder_motor" joint="shoulder" ctrllimited="true" ctrlrange="-20 20"/>
    <motor name="elbow_motor" joint="elbow" ctrllimited="true" ctrlrange="-10 10"/>
  </actuator>
</mujoco>
"""

BASE_HEIGHT, UPPER_ARM, FOREARM, HAND = 0.10, 0.12, 0.135, 0.10

FIVE_DOF_XML = f"""
<mujoco model="five_dof">
  <compiler angle="radian"/>
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <worldbody>
    <light pos="0.3 -0.5 1"/>
    <geom name="table" type="plane" size="0.5 0.5 0.05" rgba="0.9 0.9 0.9 1"/>
    <geom name="pedestal" type="cylinder" fromto="0 0 0  0 0 {BASE_HEIGHT}" size="0.03" rgba="0.3 0.3 0.3 1"/>
    <body name="shoulder" pos="0 0 {BASE_HEIGHT}">
      <joint name="shoulder_pan" type="hinge" axis="0 0 1" range="-2.0 2.0" damping="0.5"/>
      <geom type="sphere" size="0.025" mass="0.1" rgba="0.2 0.2 0.2 1"/>
      <body name="upper_arm" pos="0 0 0">
        <joint name="shoulder_lift" type="hinge" axis="0 1 0" range="-1.8 1.8" damping="0.5"/>
        <geom type="capsule" fromto="0 0 0  0 0 {UPPER_ARM}" size="0.015" mass="0.15" rgba="0.95 0.75 0.1 1"/>
        <body name="forearm" pos="0 0 {UPPER_ARM}">
          <joint name="elbow_flex" type="hinge" axis="0 1 0" range="-2.6 2.6" damping="0.5"/>
          <geom type="capsule" fromto="0 0 0  0 0 {FOREARM}" size="0.013" mass="0.12" rgba="0.95 0.75 0.1 1"/>
          <body name="wrist" pos="0 0 {FOREARM}">
            <joint name="wrist_flex" type="hinge" axis="0 1 0" range="-1.8 1.8" damping="0.2"/>
            <geom type="capsule" fromto="0 0 0  0 0 0.04" size="0.012" mass="0.06" rgba="0.2 0.2 0.2 1"/>
            <body name="hand" pos="0 0 0.04">
              <joint name="wrist_roll" type="hinge" axis="0 0 1" range="-3.0 3.0" damping="0.1"/>
              <geom type="box" pos="0 0 {(HAND - 0.04) / 2}" size="0.02 0.008 {(HAND - 0.04) / 2}" mass="0.08" rgba="0.3 0.3 0.3 1"/>
              <site name="tip" pos="0 0 {HAND - 0.04}" size="0.008" rgba="1 0 0 1"/>
            </body>
          </body>
        </body>
      </body>
    </body>
  </worldbody>
  <actuator>
    <position name="pan" joint="shoulder_pan" kp="20"/>
    <position name="lift" joint="shoulder_lift" kp="20"/>
    <position name="elbow" joint="elbow_flex" kp="20"/>
    <position name="wrist" joint="wrist_flex" kp="10"/>
    <position name="roll" joint="wrist_roll" kp="5"/>
  </actuator>
</mujoco>
"""

HOME = [0.0, 0.6, 1.2, 0.8, 0.0]     # a bent, non-singular pose of the five-joint arm [rad]


def make(xml):
    model = mujoco.MjModel.from_xml_string(xml)
    return model, mujoco.MjData(model)


def tip_pose(model, data, q):
    """Set the joint angles q and return the tip position (3,) and rotation matrix (3, 3)."""
    data.qpos[:] = q
    mujoco.mj_kinematics(model, data)
    site = model.site("tip").id
    return data.site_xpos[site].copy(), data.site_xmat[site].reshape(3, 3).copy()
