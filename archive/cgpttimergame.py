import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Reaction Time Test")

# Font
font = pygame.font.SysFont(None, 50)

def show_text(text, color, pos):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def main():
    running = True
    reaction_times = []

    while running:
        screen.fill(WHITE)
        show_text("Tap the mouse to continue", BLACK, (200, 200))
        pygame.display.flip()

        # Wait for mouse click to start the test
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False

    while len(reaction_times) < 5:
        screen.fill(RED)
        pygame.display.flip()

        # Random interval before turning green
        pygame.time.wait(random.randint(1000, 3000))

        screen.fill(GREEN)
        show_text("Click now!", BLACK, (300, 200))
        pygame.display.flip()

        # Start timer
        start_time = time.time()

        # Wait for mouse click
        reaction_time = None
        while reaction_time is None:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    end_time = time.time()
                    reaction_time = end_time - start_time

        # Record reaction time
        reaction_times.append(reaction_time)

        # Display result screen
        screen.fill(WHITE)
        show_text("Reaction Time: {:.3f} seconds".format(reaction_time), BLACK, (200, 200))
        pygame.display.flip()
        pygame.time.wait(1000)

    # Display average reaction time
    avg_reaction_time = sum(reaction_times) / len(reaction_times)
    screen.fill(WHITE)
    show_text("Average Reaction Time: {:.3f} seconds".format(avg_reaction_time), BLACK, (150, 200))
    show_text("Click to start over", BLACK, (250, 300))
    pygame.display.flip()

    # Wait for click to start over
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                reaction_times.clear()
                waiting = False

if __name__ == "__main__":
    main()
