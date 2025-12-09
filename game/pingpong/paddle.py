from dataclasses import dataclass

import pygame

from config import SCREEN_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED


@dataclass
class Paddle:
    x: int
    y: int
    up_key: int
    down_key: int
    color: tuple[int, int, int] = (50, 200, 50)

    def __post_init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, keys):
        if keys[self.up_key]:
            self.rect.y -= PADDLE_SPEED
        if keys[self.down_key]:
            self.rect.y += PADDLE_SPEED

        # bornes écran
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)
