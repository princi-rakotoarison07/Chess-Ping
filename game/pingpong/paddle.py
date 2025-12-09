from dataclasses import dataclass

import pygame

from config import SCREEN_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, BOARD_TOP, BOARD_HEIGHT


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

        # bornes : uniquement à l'intérieur du plateau
        board_top = BOARD_TOP
        board_bottom = BOARD_TOP + BOARD_HEIGHT

        if self.rect.top < board_top:
            self.rect.top = board_top
        if self.rect.bottom > board_bottom:
            self.rect.bottom = board_bottom

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)
