import pygame
import time

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

# Set the font
font = pygame.font.SysFont('Arial', 40)

# Main loop
while True:
    # Initialize the timer on mouse click
    if not hasattr(screen, 'start_time'):
        screen.start_time = time.time()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Change the color on mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            color = green if color == red else red

    # Fill the screen with the current color
    screen.fill(color)

    # Calculate the current time
    current_time = int(time.time() - screen.start_time)

    # Render the timer text
    timer_text = font.render(str(current_time), True, (0, 0, 0))
    screen.blit(timer_text, (screen_width // 2 - timer_text.get_width() // 2, 20))

    # Update the display
    pygame.display.update()

    # Check if the user closes the window
    if not pygame.display.get_surface():
        pygame.quit()
        exit()