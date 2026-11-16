// The course map. Lesson bodies live in src/content/<id>.md; a lesson without a file is "not written yet".
// Tags: 'bridge' = math bridge lesson for the student, 'review' = refresher for the parent.
// Bridge lessons sit in the track right before the lesson that needs them.

const mod = (n, title, blurb, lessons, note = '') => ({
  n,
  title,
  blurb,
  note,
  lessons: lessons.map(([id, t, tag = '']) => ({ id, title: t, tag, module: n })),
});

export const MODULES = [
  mod(0, 'Setup', 'The big picture and the tools: Python and MuJoCo.', [
    ['0.1', 'The mechatronic system'],
    ['0.2', 'Scientific Python'],
    ['0.3', 'Getting started with MuJoCo'],
  ]),
  mod(1, 'Modeling Dynamic Systems', 'Turn physics into equations you can simulate.', [
    ['B1', 'Derivatives, integrals and differential equations', 'bridge'],
    ['1.1', 'First-order systems'],
    ['1.2', 'Second-order systems'],
    ['1.3', 'Numerical integration'],
    ['B2', 'Complex numbers and Euler’s formula', 'bridge'],
    ['1.4', 'Laplace transform and transfer functions', 'review'],
    ['B3', 'Vectors, matrices, linear systems', 'bridge'],
    ['1.5', 'State-space representation'],
    ['1.6', 'Nonlinear systems and linearization'],
  ]),
  mod(2, 'Classical Control', 'Feedback, PID and how to reason about stability.', [
    ['2.1', 'The idea of feedback'],
    ['2.2', 'What each PID term does'],
    ['2.3', 'Time-domain specs and tuning'],
    ['B4', 'Eigenvalues and eigenvectors', 'bridge'],
    ['2.4', 'Stability and pole locations'],
    ['2.5', 'Frequency domain: Bode plots and margins', 'review'],
    ['2.6', 'Feedforward, windup and derivative filtering'],
    ['2.7', 'Discretization and digital PID', 'review'],
    ['2.8', 'Cascaded control loops'],
  ]),
  mod(3, 'Robot Kinematics', 'Describe where every link of an arm is, and how to get it there.', [
    ['3.1', 'Rotation matrices and Euler angles'],
    ['3.2', 'Quaternions and axis-angle'],
    ['3.3', 'Homogeneous transforms and frame chains'],
    ['3.4', 'Forward kinematics: DH and PoE'],
    ['B5', 'Partial derivatives and gradients', 'bridge'],
    ['3.5', 'The Jacobian and singularities'],
    ['3.6', 'Inverse kinematics: analytical'],
    ['3.7', 'Inverse kinematics: numerical'],
  ]),
  mod(
    4,
    'Dynamics and Arm Control',
    'Forces and torques: make an arm follow a trajectory.',
    [
      ['4.1', 'The Lagrangian method'],
      ['4.2', 'The manipulator equation'],
      ['4.3', 'Gravity compensation and feedforward'],
      ['4.4', 'Computed-torque control'],
      ['4.5', 'Trajectory generation'],
      ['4.6', 'Task-space control'],
      ['4.7', 'Impedance control and compliance'],
    ],
    'Hardware A (optional from here): SO-101 open-source arm. Code from Modules 3–4 can run on the real arm.',
  ),
  mod(5, 'Actuators and Drives', 'How motors, gearboxes and drivers really behave.', [
    ['5.1', 'Brushed DC motor model'],
    ['5.2', 'Gearboxes and reflected inertia'],
    ['5.3', 'H-bridges and PWM'],
    ['5.4', 'Brushless motors and FOC'],
    ['5.5', 'Steppers and hobby servos'],
    ['5.6', 'System identification from a step response'],
    ['5.7', 'Motor sizing'],
  ]),
  mod(6, 'Sensors and Signals', 'Measure the world, and clean up what you measure.', [
    ['6.1', 'Encoders'],
    ['6.2', 'IMUs: accelerometers and gyroscopes'],
    ['6.3', 'Range sensors'],
    ['6.4', 'Current and force sensing'],
    ['6.5', 'Sampling, aliasing and ADCs', 'review'],
    ['6.6', 'Digital filters', 'review'],
  ]),
  mod(
    7,
    'Embedded Systems',
    'Run a control loop on a microcontroller.',
    [
      ['7.1', 'Microcontroller architecture and GPIO'],
      ['7.2', 'Timers and PWM output'],
      ['7.3', 'Interrupts and real-time behavior'],
      ['7.4', 'ADC acquisition'],
      ['7.5', 'UART, I2C, SPI'],
      ['7.6', 'CAN bus'],
      ['7.7', 'A fixed-rate control loop'],
      ['7.8', 'MicroPython vs. C; RTOS concepts'],
    ],
    'Hardware B: ESP32 board, DC gear motor with encoder, TB6612 driver, servo, MPU6050, ultrasonic module.',
  ),
  mod(8, 'Modern Control', 'State-space design: pole placement, LQR, observers.', [
    ['8.1', 'Controllability and observability'],
    ['8.2', 'State feedback and pole placement'],
    ['8.3', 'LQR optimal control'],
    ['8.4', 'State observers'],
    ['8.5', 'Case study: cart-pole swing-up and balance'],
    ['8.6', 'Introduction to MPC'],
  ]),
  mod(9, 'State Estimation', 'Fuse noisy sensors into a trustworthy estimate.', [
    ['B6', 'Probability and Gaussian distributions', 'bridge'],
    ['9.1', 'Probability refresher', 'review'],
    ['9.2', 'The Bayes filter'],
    ['9.3', 'The Kalman filter'],
    ['9.4', 'The extended Kalman filter'],
    ['9.5', 'Sensor fusion: IMU and encoders'],
    ['9.6', 'Tuning Q and R'],
  ]),
  mod(10, 'Mobile Robots and Navigation', 'Localize, plan a path and follow it.', [
    ['10.1', 'Drive-base kinematics: differential, mecanum, swerve'],
    ['10.2', 'Wheel odometry'],
    ['10.3', 'Particle-filter localization'],
    ['10.4', 'Occupancy-grid mapping'],
    ['10.5', 'The idea of SLAM'],
    ['10.6', 'Path planning: A* and RRT'],
    ['10.7', 'Path tracking: pure pursuit and Stanley'],
    ['10.8', 'Obstacle avoidance and local planning'],
  ]),
  mod(11, 'ROS 2', 'The middleware that real robots are built on.', [
    ['11.1', 'Nodes, topics, services, actions'],
    ['11.2', 'tf2 coordinate transforms'],
    ['11.3', 'URDF robot descriptions'],
    ['11.4', 'ros2_control'],
    ['11.5', 'MoveIt and Nav2 overview'],
    ['11.6', 'Wrapping your controllers as ROS 2 nodes'],
  ]),
  mod(12, 'Perception and Learning', 'Cameras, reinforcement learning and sim-to-real.', [
    ['12.1', 'Camera models and calibration'],
    ['12.2', 'AprilTags and pose estimation'],
    ['12.3', 'Visual servoing'],
    ['12.4', 'Reinforcement learning basics'],
    ['12.5', 'Training policies with Gymnasium and MuJoCo'],
    ['12.6', 'Imitation learning and LeRobot'],
    ['12.7', 'Sim-to-real'],
    ['12.8', 'Combining learning with classical control'],
  ]),
];

export const LESSONS = MODULES.flatMap((m) => m.lessons);
export const lessonById = Object.fromEntries(LESSONS.map((l) => [l.id, l]));
export const moduleByN = Object.fromEntries(MODULES.map((m) => [m.n, m]));

export const TAG_LABEL = { bridge: 'Bridge', review: 'Review' };

// Bridge lessons are part of the student's track only; the parent can still open them.
export const inTrack = (lesson, learner) => lesson.tag !== 'bridge' || learner !== 'parent';

export const track = (learner) => LESSONS.filter((l) => inTrack(l, learner));

export function label(lesson) {
  return lesson.tag === 'bridge' ? `Bridge ${lesson.id}` : lesson.id;
}
