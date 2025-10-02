import math
import random
import pygame
import time

pygame.init()

Width, Height = 700, 500
Win = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Aim Trainer")

def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        # limit fps so the loop doesn't spin too fast
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # draw something so the window stays responsive
        Win.fill((0, 0, 0))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
