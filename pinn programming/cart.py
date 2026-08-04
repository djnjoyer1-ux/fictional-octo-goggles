import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

t = np.linspace(0,10,200)

x = 2 * np.sin(t)

fig,ax = plt.subplots()
ax.set_xlim(-3,3)
ax.set_ylim(-1,10)

cart_width = 0.6
cart_height = 0.3
cart = plt.Rectangle((0,-0.15), cart_width, cart_height, color='black')
ax.add_patch(cart)


ax.plot([-5,5],[-.2,-.2])


def update(frame):
    cart.set_x(x[frame]-cart_width/2)
    return cart,

ani = FuncAnimation(fig,update,frames=len(t), interval = 50, blit = True)




plt.show()
