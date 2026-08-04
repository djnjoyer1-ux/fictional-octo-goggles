import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Time
t = np.linspace(0, 10, 200)

# Cart motion
x = 2 * np.sin(t)

# Pendulum motion (just for visualization)
theta = 0.5 * np.sin(2 * t)  # angle in radians

# Pendulum length
L = 1.0

# Set up figure
fig, ax = plt.subplots()
ax.set_xlim(-3, 3)
ax.set_ylim(-1, 2)

# Cart
cart_width = 0.6
cart_height = 0.3
cart = plt.Rectangle((0, -0.15), cart_width, cart_height, color='black')
ax.add_patch(cart)

# Pendulum line
line, = ax.plot([], [], linewidth=2)

# Pendulum mass (dot)
mass, = ax.plot([], [], 'o')

# Ground
ax.plot([-5, 5], [-0.2, -0.2])

# Animation update
def update(frame):
    # Cart position
    xc = x[frame]
    yc = 0

    # Update cart
    cart.set_x(xc - cart_width / 2)

    # Pendulum pivot (top of cart)
    px = xc
    py = yc + cart_height / 2

    # Pendulum end
    pend_x = px + L * np.sin(theta[frame])
    pend_y = py - L * np.cos(theta[frame])

    # Update pendulum line
    line.set_data([px, pend_x], [py, pend_y])

    # Update mass
    mass.set_data([pend_x], [pend_y])

    return cart, line, mass

# Animate
ani = FuncAnimation(fig, update, frames=len(t), interval=50, blit=True)

plt.title("Cart + Pendulum (Kinematic Animation)")
plt.show()
