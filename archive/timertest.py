import pygame

# Initialize Pygame
pygame.init()

# Set the screen size
screen_width = 800
screen_height = 600

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title and icon
pygame.display.set_caption("Color Changer")

# Set the colors
red = (255, 0, 0)
green = (0, 255, 0)

# Set the initial color
color = red

# Set the event list
event_list = pygame.event.get()

# Main loop
while True:
    # Handle events
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Change the color on mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            color = green if color == red else red

    # Fill the screen with the current color
    screen.fill(color)

    # Update the display
    pygame.display.update()

    # Get the event list for the next iteration
    event_list = pygame.event.get()