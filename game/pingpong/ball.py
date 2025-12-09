import random

import pygame

from config import (
    SCREEN_WIDTH,
    BALL_RADIUS,
    BALL_SPEED_X,
    BALL_SPEED_Y,
    BOARD_LEFT,
    BOARD_TOP,
    BOARD_WIDTH,
    BOARD_HEIGHT,
)


class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.color = (0, 0, 0)  # noir par défaut
        self.reset()

    def reset(self):
        # centre du plateau
        self.x = BOARD_LEFT + BOARD_WIDTH // 2
        self.y = BOARD_TOP + BOARD_HEIGHT // 2
        self.vx = random.choice([-1, 1]) * BALL_SPEED_X
        self.vy = random.choice([-1, 1]) * BALL_SPEED_Y
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = (self.x, self.y)
        self.color = (0, 0, 0)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

        # Limites du plateau
        board_left = BOARD_LEFT
        board_right = BOARD_LEFT + BOARD_WIDTH
        board_top = BOARD_TOP
        board_bottom = BOARD_TOP + BOARD_HEIGHT

        # rebond haut / bas sur les bords du plateau
        if self.rect.top <= board_top:
            self.rect.top = board_top
            self.y = self.rect.centery
            self.vy *= -1
        elif self.rect.bottom >= board_bottom:
            self.rect.bottom = board_bottom
            self.y = self.rect.centery
            self.vy *= -1

        # rebond gauche / droite sur les bords du plateau
        if self.rect.left <= board_left:
            self.rect.left = board_left
            self.x = self.rect.centerx
            self.vx *= -1
        elif self.rect.right >= board_right:
            self.rect.right = board_right
            self.x = self.rect.centerx
            self.vx *= -1

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
