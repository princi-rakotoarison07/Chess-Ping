import random

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, BALL_RADIUS, BALL_SPEED_X, BALL_SPEED_Y


class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.color = (0, 0, 0)  # noir par défaut
        self.reset()

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vx = random.choice([-1, 1]) * BALL_SPEED_X
        self.vy = random.choice([-1, 1]) * BALL_SPEED_Y
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = (self.x, self.y)
        self.color = (0, 0, 0)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

        # rebond haut / bas
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy *= -1

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
