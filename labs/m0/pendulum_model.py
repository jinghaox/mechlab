"""The pendulum model shared by the Lab 0.3 scripts."""

LENGTH = 0.5   # metres, pivot to centre of the bob
GRAVITY = 9.81

PENDULUM_XML = f"""
<mujoco model="pendulum">
  <option timestep="0.002" gravity="0 0 -{GRAVITY}" integrator="RK4"/>

  <worldbody>
    <light pos="0 -1 2"/>
    <geom name="floor" type="plane" size="1 1 0.1" pos="0 0 -0.8" rgba="0.9 0.9 0.9 1"/>

    <body name="pendulum" pos="0 0 0">
      <joint name="hinge" type="hinge" axis="0 1 0" damping="0"/>
      <geom name="rod" type="capsule" fromto="0 0 0  0 0 -{LENGTH}" size="0.01" mass="0.02"/>
      <geom name="bob" type="sphere" pos="0 0 -{LENGTH}" size="0.05" mass="1"/>
    </body>
  </worldbody>

  <sensor>
    <jointpos name="angle" joint="hinge"/>
    <jointvel name="rate" joint="hinge"/>
  </sensor>
</mujoco>
"""
