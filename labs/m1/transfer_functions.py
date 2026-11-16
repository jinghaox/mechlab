"""Lab 1.4 - Transfer functions, poles and step responses with python-control."""
import control as ct
import matplotlib.pyplot as plt
import numpy as np

wn = 10.0   # rad/s, the mass-spring-damper from Lab 1.2
t = np.linspace(0, 6, 6001)

fig, (ax_poles, ax_step) = plt.subplots(1, 2, figsize=(11, 4.5))

print(" zeta   poles                           overshoot   settling (2%)   DC gain")
for zeta in [0.1, 0.4, 0.7, 1.0, 2.0]:
    # G(s) = wn^2 / (s^2 + 2 zeta wn s + wn^2)
    G = ct.tf([wn**2], [1, 2 * zeta * wn, wn**2])
    poles = ct.poles(G)
    info = ct.step_info(G, T=t)
    pole_text = ", ".join(f"{p.real:6.2f}{p.imag:+6.2f}j" for p in poles)
    print(f" {zeta:4.1f}   {pole_text:30s}  {info['Overshoot']:6.1f} %      {info['SettlingTime']:.3f} s       {ct.dcgain(G):.2f}")

    _, y = ct.step_response(G, t)
    line, = ax_step.plot(t, y, label=f"zeta = {zeta}")
    ax_poles.plot(poles.real, poles.imag, "x", ms=9, mew=2, color=line.get_color())

ax_poles.axvline(0, color="k", lw=0.8)
ax_poles.axhline(0, color="k", lw=0.8)
ax_poles.set_xlabel("real part  (decay rate)")
ax_poles.set_ylabel("imaginary part  (oscillation frequency)")
ax_poles.set_title("Poles in the s-plane")
ax_poles.grid(True)
ax_step.set_xlabel("time [s]")
ax_step.set_xlim(0, 3)
ax_step.set_title("Step responses")
ax_step.legend()
ax_step.grid(True)

# --- Block algebra: a motor (voltage -> speed) followed by an integrator (speed -> angle) ---
motor = ct.tf([50], [0.2, 1])       # 50 / (0.2 s + 1), the motor from Lab 1.1
integrator = ct.tf([1], [1, 0])     # 1 / s
voltage_to_angle = ct.series(motor, integrator)
print("\nvoltage -> angle:", voltage_to_angle)
print("poles:", ct.poles(voltage_to_angle))

# Close a loop around it:  u = Kp * (r - angle)
Kp = 0.1
closed = ct.feedback(Kp * voltage_to_angle, 1)
print(f"closed loop with Kp = {Kp}: poles = {ct.poles(closed)}, DC gain = {ct.dcgain(closed):.2f}")

plt.tight_layout()
plt.show()
