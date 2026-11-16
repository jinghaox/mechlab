# Mechatronics & Robotics Curriculum

## 1. Learners and goal

| Learner | Background | Gaps to fill |
|---|---|---|
| Parent | Circuits, digital and analog electronics; C and Python; calculus, linear algebra, random processes, signal processing (partly forgotten) | Control theory, motors and drives, embedded real-time programming, robotics |
| Student (grade 11) | FTC / FRC competition experience, COSMOS robotics summer program; hands-on and programming experience | Theory; math tools such as linear algebra, complex numbers, differential equations, probability |

**Goal**: be able to carry out the full workflow of modeling → simulation → controller design → state estimation → real hardware, and move control code written in MuJoCo onto a real robot arm, then a mobile robot.

**Language**: all lesson content, quizzes and lab instructions are in English.

## 2. Format

- **Phone app**: lessons (15–20 minutes each), formulas and figures, quizzes, AI tutor.
- **PC labs**: every module has Python labs using NumPy / SciPy / python-control / MuJoCo. The app provides the task description and starter code.
- **Hardware labs**: the arm after Module 4, the microcontroller kit after Module 7. Wokwi (online simulator) can stand in for the microcontroller until the kit arrives.

**One main track, three kinds of tags** (both learners share the same track):

- `[Bridge]` math bridge lessons: for the student; the parent can skip them.
- `[Review]` refresher lessons: help the parent recover forgotten material; new material for the student, to be taken slowly together with the matching bridge lesson.
- `FRC link`: connects the theory to things already used in FTC/FRC (WPILib PID, feedforward, pose estimation, swerve, and so on).

## 3. Order and dependencies

The track is arm-first: manipulators come right after the control basics, mobile robots later.

```
0 Setup → 1 Modeling → 2 Classical Control
        → 3 Kinematics → 4 Dynamics & Arm Control → [Hardware A: arm]
        → 5 Actuators → 6 Sensors → 7 Embedded → [Hardware B: MCU kit]
        → 8 Modern Control → 9 State Estimation
        → 10 Mobile Robots → 11 ROS 2 → 12 Perception & Learning → Capstone
```

Hard prerequisites: 3 needs 1; 4 needs 2 and 3; 7 needs 5 and 6; 8 needs 2; 9 needs 8; 10 needs 9; 12 needs 3 and 4.

## 4. Math bridge lessons `[Bridge]`

Inserted where the main track needs them, not front-loaded.

| No. | Content | Take before |
|---|---|---|
| B1 | Intuition for derivatives, integrals and differential equations | 1.1 |
| B2 | Complex numbers and Euler's formula | 1.4 |
| B3 | Vectors, matrices, linear systems | 1.5 |
| B4 | Eigenvalues and eigenvectors | 2.4 |
| B5 | Multivariable functions, partial derivatives, gradients | 3.5 |
| B6 | Probability, expectation, variance, Gaussian distributions | 9.1 |

## 5. Main track

### Module 0 — Setup (3 lessons)

- 0.1 The mechatronic system: the sense → control → actuate loop; course roadmap
- 0.2 Scientific Python: NumPy, SciPy, Matplotlib, python-control
- 0.3 Getting started with MuJoCo: MJCF models, the simulation loop, the viewer

**Lab**: build a pendulum in MuJoCo, log its angle and plot energy over time.

### Module 1 — Modeling Dynamic Systems (6 lessons)

- 1.1 First-order systems: RC circuit and motor speed; the time constant
- 1.2 Second-order systems: mass-spring-damper; natural frequency and damping ratio
- 1.3 Numerical integration: Euler, RK4, step size and numerical stability
- 1.4 `[Review]` Laplace transform and transfer functions; poles and zeros
- 1.5 State-space representation: from differential equations to ẋ = Ax + Bu
- 1.6 Nonlinear systems and linearization: the pendulum

**Lab**: write your own pendulum simulator (RK4) and compare it with MuJoCo.

### Module 2 — Classical Control (8 lessons)

- 2.1 The idea of feedback: open loop vs. closed loop
- 2.2 What each PID term does
- 2.3 Time-domain specs: rise time, overshoot, steady-state error; tuning methods
- 2.4 Stability: pole locations and system behavior; root-locus intuition
- 2.5 `[Review]` Frequency domain: Bode plots, gain margin, phase margin
- 2.6 Practical issues: feedforward, integral windup, derivative noise and filtering
- 2.7 `[Review]` Discretization: sampling, zero-order hold, digital PID
- 2.8 Cascaded control: current, velocity and position loops

**Lab**: single-joint position control in MuJoCo; stabilize an inverted pendulum with PID.
**FRC link**: what WPILib's `PIDController` and the kS / kV / kA feedforward gains mean physically.

### Module 3 — Robot Kinematics (7 lessons)

- 3.1 Rigid-body orientation: rotation matrices, Euler angles, gimbal lock
- 3.2 Quaternions and axis-angle
- 3.3 Homogeneous transforms and frame chains
- 3.4 Forward kinematics: DH parameters and product of exponentials (PoE)
- 3.5 The Jacobian: velocity mapping, force mapping, singularities
- 3.6 Inverse kinematics: analytical solutions
- 3.7 Inverse kinematics: numerical solutions (Jacobian pseudoinverse, damped least squares)

**Lab**: forward and inverse kinematics of a planar two-link arm in MuJoCo, then numerical IK on the SO-101 arm model so the end effector traces a circle.
**FRC link**: kinematics of arm, wrist and elevator mechanisms.

### Module 4 — Dynamics and Arm Control (7 lessons)

- 4.1 The Lagrangian method
- 4.2 The manipulator equation: inertia matrix, Coriolis terms, gravity terms
- 4.3 Gravity compensation and feedforward
- 4.4 Computed-torque control
- 4.5 Trajectory generation: polynomial interpolation, trapezoidal velocity profiles
- 4.6 Task-space control
- 4.7 Impedance control and compliance

**Lab**: read M, C and g from MuJoCo, implement gravity compensation and computed-torque control, and track a trajectory.
**FRC link**: `TrapezoidProfile` and gravity feedforward for arms and elevators.

> **Hardware A — robot arm** (roughly ¥1000–2000): SO-101 open-source arm. It has a MuJoCo model, so code from Modules 3 and 4 can be verified on the real arm. It is driven from Python on the PC, so it does not need the embedded module first. Optional at this point; it can also wait until Module 12.

### Module 5 — Actuators and Drives (7 lessons)

- 5.1 Brushed DC motor model: electrical and mechanical equations; torque-speed curve
- 5.2 Gearboxes: ratio, reflected inertia, efficiency and backlash
- 5.3 H-bridges and PWM drive
- 5.4 Brushless motors and the basics of FOC
- 5.5 Stepper motors and hobby servos
- 5.6 System identification: estimating motor parameters from a step response
- 5.7 Motor sizing: power, torque and gear ratio from load and motion requirements

**Lab**: simulate a full DC motor model in Python, identify its parameters from data and design a velocity loop.
**FRC link**: motor curves (stall torque, free speed) and choosing gear ratios for a mechanism.

### Module 6 — Sensors and Signals (6 lessons)

- 6.1 Encoders: incremental and absolute, quadrature decoding, velocity measurement
- 6.2 IMUs: accelerometers and gyroscopes; noise, bias and drift
- 6.3 Range sensors: ultrasonic, time-of-flight, lidar
- 6.4 Current and force sensing
- 6.5 `[Review]` Sampling and aliasing; ADC resolution and quantization
- 6.6 `[Review]` Digital filters: low-pass, moving average, complementary filter

**Lab**: add noise and bias to MuJoCo IMU data and estimate orientation with a complementary filter.

### Module 7 — Embedded Systems (8 lessons)

Wokwi simulation first; repeat on real hardware once the kit arrives.

- 7.1 Microcontroller architecture and GPIO
- 7.2 Timers and PWM output
- 7.3 Interrupts and real-time behavior
- 7.4 ADC acquisition
- 7.5 UART, I2C, SPI
- 7.6 CAN bus
- 7.7 Implementing a fixed-rate control loop: period, jitter, computation delay
- 7.8 MicroPython vs. C; basic RTOS concepts

**Lab**: read an encoder → compute speed → PID → PWM output, closing a motor velocity loop.
**FRC link**: the robot's CAN network; where the 20 ms control period comes from.

> **Hardware B — microcontroller kit** (roughly ¥100–200): ESP32 dev board, DC gear motor with encoder, TB6612 driver board, hobby servo, MPU6050, ultrasonic module, breadboard and jumper wires.

### Module 8 — Modern Control (6 lessons)

- 8.1 State space revisited; controllability and observability
- 8.2 State feedback and pole placement
- 8.3 LQR optimal control
- 8.4 State observers
- 8.5 Case study: swing-up and balance of a cart-pole
- 8.6 Introduction to model predictive control (MPC)

**Lab**: cart-pole in MuJoCo; compare PID, pole placement and LQR.
**FRC link**: WPILib's state-space controllers (`LinearSystemLoop`).

### Module 9 — State Estimation (6 lessons)

- 9.1 `[Review]` Probability refresher: Gaussians, covariance, conditional probability
- 9.2 The Bayes filter framework: predict and update
- 9.3 The Kalman filter: derivation and implementation
- 9.4 The extended Kalman filter (EKF)
- 9.5 Sensor fusion: IMU and encoders
- 9.6 Tuning: the meaning of process noise Q and measurement noise R

**Lab**: fuse noisy position and acceleration with a Kalman filter; estimate a differential-drive robot's pose with an EKF.
**FRC link**: how `SwerveDrivePoseEstimator` fuses odometry and vision.

### Module 10 — Mobile Robots and Navigation (8 lessons)

- 10.1 Drive-base kinematics: differential, mecanum, swerve
- 10.2 Wheel odometry and error accumulation
- 10.3 Particle-filter localization
- 10.4 Occupancy-grid mapping
- 10.5 The basic idea of SLAM
- 10.6 Path planning: A*, RRT
- 10.7 Path tracking: pure pursuit, Stanley
- 10.8 Obstacle avoidance and local planning

**Lab**: complete localization → planning → tracking in a 2D Python simulation.
**FRC link**: swerve module state calculation; the principles behind autonomous path following (PathPlanner).

### Module 11 — ROS 2 (6 lessons)

- 11.1 Nodes, topics, services, actions
- 11.2 tf2 coordinate transforms
- 11.3 URDF robot descriptions
- 11.4 ros2_control
- 11.5 Overview of MoveIt and Nav2
- 11.6 Wrapping earlier controllers as ROS 2 nodes

**Lab**: turn the Module 3 inverse kinematics into a ROS 2 node that drives the simulated arm.

### Module 12 — Perception and Learning (8 lessons)

- 12.1 Camera models and calibration
- 12.2 AprilTags and pose estimation
- 12.3 Visual servoing
- 12.4 Reinforcement learning basics: MDPs, policies, value functions
- 12.5 Training policies with Gymnasium and MuJoCo (PPO)
- 12.6 Imitation learning and LeRobot
- 12.7 Sim-to-real: domain randomization, modeling delay and noise
- 12.8 Combining learning with classical control

**Lab**: train a reaching or balancing task with PPO in MuJoCo.
**FRC link**: how field AprilTag localization works.

### Capstone projects (pick one or more)

- **A — Arm pick-and-place** (needs SO-101): inverse kinematics and trajectory planning in simulation → real arm → add vision or imitation learning. Uses Modules 3, 4, 12.
- **B — Self-balancing robot** (Hardware B parts are enough): modeling → LQR → complementary or Kalman filter → implementation on the ESP32. Uses Modules 1, 2, 5–9.
- **C — Autonomous navigation robot** (needs a ROS 2 rover with lidar, an optional later purchase): mapping, localization, planning, tracking. Uses Modules 9–11.

## 6. Size and pace

- 86 main-track lessons plus 6 bridge lessons, 92 in total.
- At 3–4 lessons and one lab per week, about 6–7 months.
- First milestone: Modules 0–2 (17 lessons, about 5 weeks) — stabilize an inverted pendulum in MuJoCo.
- Second milestone: Modules 3–4 (14 lessons, about 4 weeks) — a simulated arm tracks a trajectory under computed-torque control.

## 7. Lesson structure (for app development)

Each lesson has: title and module, prerequisites, tag (`[Bridge]` / `[Review]`), body (Markdown + LaTeX), figures, key-formula summary, quiz (3–5 questions), PC lab (if any), FRC link (if any). When the AI tutor is called, the current lesson body and the learner profile are sent as context.
