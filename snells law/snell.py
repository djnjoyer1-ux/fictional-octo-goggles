import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Constants
n_glass = 1.5  # Refractive index for the glass
n_steel = 3.0  # Refractive index for the steel
n_air = 1.0    # Refractive index for air (background)
angle_incident = np.radians(30)  # Angle of incoming light in radians

# Geometry of the system
core_radius = 0.1  # Radius of the steel core
length = 5         # Length of the area where light will travel
num_rays = 5       # Number of light rays to simulate

# Create a figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-length, length)
ax.set_ylim(-length, length)
ax.set_aspect('equal')

# Draw the transparent material and the steel core
circle = patches.Circle((0, 0), core_radius, edgecolor='black', facecolor='gray', alpha=0.5)
ax.add_patch(circle)

# Function to apply Snell's Law and calculate refraction
def snell_law(theta1, n1, n2):
    """Calculates the refracted angle using Snell's Law"""
    return np.arcsin(n1 * np.sin(theta1) / n2)

# Function to plot a ray and trace its path through different media
def plot_ray(ax, angle, start_x, start_y, n1, n2, color='blue'):
    """Plots a ray passing through the media with refraction at interfaces"""
    # Initial ray in air
    x1, y1 = start_x, start_y
    dx1 = np.cos(angle)
    dy1 = np.sin(angle)

    # Calculate where ray hits the boundary of the steel core
    t = core_radius / np.sqrt(dx1**2 + dy1**2)
    x2 = x1 + dx1 * t
    y2 = y1 + dy1 * t

    # Refract inside the core
    angle_refracted = snell_law(angle, n1, n2)
    dx2 = np.cos(angle_refracted)
    dy2 = np.sin(angle_refracted)

    # Extend the ray inside the steel core
    t_core = length  # Length within the steel core
    x3 = x2 + dx2 * t_core
    y3 = y2 + dy2 * t_core

    # Refract back into the glass (air) region
    angle_back = snell_law(angle_refracted, n2, n1)
    dx3 = np.cos(angle_back)
    dy3 = np.sin(angle_back)

    # Extend the ray outside the core (return to air)
    t_air = length  # Length outside the core
    x4 = x3 + dx3 * t_air
    y4 = y3 + dy3 * t_air

    # Plotting the rays
    ax.plot([x1, x2], [y1, y2], color=color)  # First segment (air -> core)
    ax.plot([x2, x3], [y2, y3], color=color)  # Second segment (core)
    ax.plot([x3, x4], [y3, y4], color=color)  # Third segment (core -> air)

# Plot multiple rays with different initial angles
for i in range(num_rays):
    angle_offset = np.radians(i * 10)  # Slightly different angles
    plot_ray(ax, angle_incident + angle_offset, -length, -length, n_air, n_glass)

# Labels and customization
ax.set_title("Light Bending Around a Thin Steel Core (2D Slice)")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.axhline(0, color='black',linewidth=0.5)
ax.axvline(0, color='black',linewidth=0.5)
ax.grid(True, linestyle='--', alpha=0.5)

# Show plot
plt.show()
