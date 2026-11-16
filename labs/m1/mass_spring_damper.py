"""Lab 1.2 - Step response of a mass-spring-damper for several damping ratios.

Standard form:  x'' + 2*zeta*wn*x' + wn^2 * x = wn^2 * u
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

m = 1.0      # kg
k = 100.0    # N/m
wn = np.sqrt(k / m)   # natural frequency [rad/s]

ZETAS = [0.1, 0.4, 0.7, 1.0, 2.0]
t = np.linspace(0, 6, 6001)


def simulate(zeta):
    def f(t, x):
        pos, vel = x
        u = 1.0
        return [vel, wn**2 * (u - pos) - 2 * zeta * wn * vel]

    sol = solve_ivp(f, (t[0], t[-1]), [0.0, 0.0], t_eval=t, rtol=1e-9, atol=1e-12)
    return sol.y[0]


print(f"wn = {wn:.1f} rad/s  ({wn / (2 * np.pi):.2f} Hz)")
print(" zeta   c [N s/m]   overshoot   formula   peak time   formula   2% settling")
for zeta in ZETAS:
    x = simulate(zeta)
    c = 2 * zeta * np.sqrt(k * m)
    overshoot = max(x.max() - 1.0, 0.0)
    outside = np.where(np.abs(x - 1.0) > 0.02)[0]
    settle = t[min(outside[-1] + 1, len(t) - 1)] if len(outside) else 0.0
    if zeta < 1:
        wd = wn * np.sqrt(1 - zeta**2)
        formula_os = f"{100 * np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2)):6.1f} %"
        peak, formula_tp = f"{t[x.argmax()]:.3f} s", f"{np.pi / wd:.3f} s"
    else:
        formula_os, peak, formula_tp = "   none", "   -   ", "   -   "
    print(f" {zeta:4.1f}   {c:8.1f}    {100 * overshoot:6.1f} %   {formula_os}    {peak}    {formula_tp}     {settle:.3f} s")
    plt.plot(t, x, label=f"zeta = {zeta}")

plt.axhline(1.0, color="gray", lw=0.8)
plt.xlim(0, 3)
plt.xlabel("time [s]")
plt.ylabel("position [m]")
plt.title("Mass-spring-damper step response")
plt.legend()
plt.grid(True)
plt.show()
