import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define the true function for f(x) and the exact solution u(x)
def f(x):
    return (torch.pi**2) * torch.sin(torch.pi * x)

def exact_solution(x):
    return torch.sin(torch.pi * x)

# 1. Define the neural network
class PINN(nn.Module):
    def __init__(self):
        super(PINN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 32),
            nn.Tanh(),
            nn.Linear(32, 32),
            nn.Tanh(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x)

# 2. Define the physics loss function
def physics_loss(model, x):
    x.requires_grad = True
    u = model(x)

    # First derivative: du/dx
    du = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]

    # Second derivative: d²u/dx²
    d2u = torch.autograd.grad(du, x, grad_outputs=torch.ones_like(du), create_graph=True)[0]

    # Physics residual: d²u/dx² + f(x)
    residual = d2u + f(x)
    return torch.mean(residual**2)

# 3. Define the boundary loss function
def boundary_loss(model):
    x0 = torch.tensor([[0.0]], device=device)
    x1 = torch.tensor([[1.0]], device=device)
    u0 = model(x0)
    u1 = model(x1)
    return (u0**2 + u1**2).mean()

# 4. Training loop
model = PINN().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
epochs = 5000

for epoch in range(epochs):
    x = torch.linspace(0, 1, 100).view(-1, 1).to(device)

    p_loss = physics_loss(model, x)
    b_loss = boundary_loss(model)
    loss = p_loss + b_loss

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 500 == 0:
        print(f"Epoch {epoch}: Total Loss = {loss.item():.5f}, Physics = {p_loss.item():.5f}, BC = {b_loss.item():.5f}")

# 5. Plot results
x_test = torch.linspace(0, 1, 100).view(-1, 1).to(device)
u_pred = model(x_test).detach().cpu()
u_true = exact_solution(x_test).detach().cpu()

plt.plot(x_test.cpu(), u_pred, label='PINN Prediction')
plt.plot(x_test.cpu(), u_true, '--', label='Exact Solution')
plt.xlabel('x')
plt.ylabel('u(x)')
plt.legend()
plt.title('1D Poisson Equation Solved by PINN')
plt.grid(True)
plt.show()
