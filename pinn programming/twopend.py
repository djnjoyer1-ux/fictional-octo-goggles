import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib.animation import FuncAnimation

# -----------------------------
# Parameters
# -----------------------------
g = 9.81
m1, m2 = 1.0, 1.0
l1, l2 = 1.0, 1.0
c1, c2 = 0.1, 0.1   # damping

# -----------------------------
# Equations of Motion
# -----------------------------
def double_pendulum(t, y):
    theta1, omega1, theta2, omega2 = y

    delta = theta1 - theta2

    denom1 = (m1 + m2)*l1 - m2*l1*np.cos(delta)**2
    denom2 = (l2/l1) * denom1

    # θ1 double dot
    num1 = (
        -m2*l1*omega1**2*np.sin(delta)*np.cos(delta)
        + m2*g*np.sin(theta2)*np.cos(delta)
        + m2*l2*omega2**2*np.sin(delta)
        - (m1 + m2)*g*np.sin(theta1)
        - c1*omega1
    )
    alpha1 = num1 / denom1

    # θ2 double dot
    num2 = (
        (m1 + m2)*l1*omega1**2*np.sin(delta)
        - (m1 + m2)*g*np.sin(theta2)
        + (m1 + m2)*g*np.sin(theta1)*np.cos(delta)
        - m2*l2*omega2**2*np.sin(delta)*np.cos(delta)
        - c2*omega2
    )
    alpha2 = num2 / denom2

    return [omega1, alpha1, omega2, alpha2]

# -----------------------------
# Initial Conditions
# -----------------------------
y0 = [np.pi/2, 0, np.pi/2 + 0.01, 0]  # small offset → chaos

t_span = (0, 20)
t_eval = np.linspace(*t_span, 1000)

# Solve ODE
sol = solve_ivp(double_pendulum, t_span, y0, t_eval=t_eval)

theta1 = sol.y[0]
theta2 = sol.y[2]

# -----------------------------
# Convert to Cartesian coords
# -----------------------------
x1 = l1 * np.sin(theta1)
y1 = -l1 * np.cos(theta1)

x2 = x1 + l2 * np.sin(theta2)
y2 = y1 - l2 * np.cos(theta2)

# -----------------------------
# Plot angles vs time
# -----------------------------
plt.figure()
plt.plot(sol.t, theta1, label='theta1')
plt.plot(sol.t, theta2, label='theta2')
plt.xlabel('Time (s)')
plt.ylabel('Angle (rad)')
plt.legend()
plt.title("Angles vs Time")
plt.show()

# -----------------------------
# Animation
# -----------------------------
fig, ax = plt.subplots()
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)

line, = ax.plot([], [], 'o-', lw=2)

def update(frame):
    line.set_data([0, x1[frame], x2[frame]],
                  [0, y1[frame], y2[frame]])
    return line,

ani = FuncAnimation(fig, update, frames=len(t_eval), interval=20)
plt.title("Double Pendulum")
plt.show()