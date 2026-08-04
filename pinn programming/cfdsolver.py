import numpy as np
import matplotlib.pyplot as plt

# ------------------------
# Parameters
# ------------------------
Nx, Ny = 50, 50
Lx, Ly = 1.0, 1.0
dx, dy = Lx/Nx, Ly/Ny

rho = 1.0
nu = 0.01
dt = 0.001
nt = 500   # time steps
nit = 50   # pressure iterations per step

# ------------------------
# Fields
# ------------------------
u_field = np.zeros((Ny, Nx))
v_field = np.zeros((Ny, Nx))
p = np.zeros((Ny, Nx))

# ------------------------
# Helper: Pressure Poisson
# ------------------------
def pressure_poisson(p, u, v):
    pn = p.copy()

    for _ in range(nit):
        pn = p.copy()

        p[1:-1,1:-1] = (
            (pn[1:-1,2:] + pn[1:-1,0:-2]) * dy**2 +
            (pn[2:,1:-1] + pn[0:-2,1:-1]) * dx**2
        ) / (2*(dx**2 + dy**2)) - (
            rho * dx**2 * dy**2 / (2*(dx**2 + dy**2) * dt)
        ) * (
            (u[1:-1,2:] - u[1:-1,0:-2])/(2*dx) +
            (v[2:,1:-1] - v[0:-2,1:-1])/(2*dy)
        )

        # Pressure boundary conditions
        p[:,-1] = p[:,-2]   # dp/dx = 0
        p[:,0]  = p[:,1]
        p[0,:]  = p[1,:]
        p[-1,:] = 0.0       # reference pressure

    return p

# ------------------------
# Time stepping loop
# ------------------------
for n in range(nt):
    un = u_field.copy()
    vn = v_field.copy()

    # ------------------------
    # Step 1: Momentum (u*, v*)
    # ------------------------
    u_field[1:-1,1:-1] = (
        un[1:-1,1:-1]
        - dt/dx * un[1:-1,1:-1]*(un[1:-1,1:-1] - un[1:-1,0:-2])
        - dt/dy * vn[1:-1,1:-1]*(un[1:-1,1:-1] - un[0:-2,1:-1])
        + nu * dt * (
            (un[1:-1,2:] - 2*un[1:-1,1:-1] + un[1:-1,0:-2]) / dx**2 +
            (un[2:,1:-1] - 2*un[1:-1,1:-1] + un[0:-2,1:-1]) / dy**2
        )
    )

    v_field[1:-1,1:-1] = (
        vn[1:-1,1:-1]
        - dt/dx * un[1:-1,1:-1]*(vn[1:-1,1:-1] - vn[1:-1,0:-2])
        - dt/dy * vn[1:-1,1:-1]*(vn[1:-1,1:-1] - vn[0:-2,1:-1])
        + nu * dt * (
            (vn[1:-1,2:] - 2*vn[1:-1,1:-1] + vn[1:-1,0:-2]) / dx**2 +
            (vn[2:,1:-1] - 2*vn[1:-1,1:-1] + vn[0:-2,1:-1]) / dy**2
        )
    )

    # ------------------------
    # Step 2: Pressure solve
    # ------------------------
    p = pressure_poisson(p, u_field, v_field)

    # ------------------------
    # Step 3: Velocity correction
    # ------------------------
    u_field[1:-1,1:-1] -= dt/rho * (p[1:-1,2:] - p[1:-1,0:-2])/(2*dx)
    v_field[1:-1,1:-1] -= dt/rho * (p[2:,1:-1] - p[0:-2,1:-1])/(2*dy)

    # ------------------------
    # Step 4: Boundary conditions
    # ------------------------
    u_field[0,:] = 0
    u_field[:,0] = 0
    u_field[:,-1] = 0
    u_field[-1,:] = 1.0   # moving lid

    v_field[0,:] = 0
    v_field[-1,:] = 0
    v_field[:,0] = 0
    v_field[:,-1] = 0

# ------------------------
# Plot results
# ------------------------
X, Y = np.meshgrid(np.linspace(0,1,Nx), np.linspace(0,1,Ny))

plt.figure(figsize=(6,5))
plt.contourf(X, Y, u_field, 50)
plt.colorbar(label="u velocity")
plt.quiver(X[::3,::3], Y[::3,::3],
           u_field[::3,::3], v_field[::3,::3])
plt.title("Lid-Driven Cavity Flow")
plt.xlabel("x")
plt.ylabel("y")
plt.show()