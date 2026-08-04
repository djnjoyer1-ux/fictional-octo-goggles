import numpy as np
import matplotlib.pyplot as plt

# Cantilever beam properties
L = 2.0          # length of beam, meters
P = 100.0        # point load at free end, Newtons
E = 200e9        # Young's modulus, Pa
I = 1e-6         # second moment of area, m^4

# Beam coordinate
x = np.linspace(0, L, 300)

# Deflection equation for cantilever with end point load:
# y(x) = P*x^2*(3L - x) / (6EI)
y = (P * x**2 * (3*L - x)) / (6 * E * I)

# Max deflection at free end:
y_max = (P * L**3) / (3 * E * I)

print(f"Maximum deflection: {y_max:.6e} m")

# Plot
plt.figure(figsize=(8, 4))
plt.plot(x, -y, linewidth=3, label="Deflected shape")
plt.axhline(0, linestyle="--", label="Original beam")

plt.scatter([0], [0], s=80, label="Fixed end")
plt.scatter([L], [-y_max], s=80, label="Free end")

plt.title("Cantilever Beam Deflection with End Point Load")
plt.xlabel("Beam length x (m)")
plt.ylabel("Deflection y (m)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
