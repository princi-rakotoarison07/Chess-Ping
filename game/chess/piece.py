from dataclasses import dataclass
from typing import Tuple

import pygame

from config import PIECE_LIFE
from utils.loader import load_image


@dataclass
class Piece:
    kind: str  # "pawn", "rook", "knight", "bishop", "queen", "king"
    color: str  # "white" ou "dark"
    position: Tuple[int, int]

    def __post_init__(self):
        self.max_life = PIECE_LIFE.get(self.kind, 1)
        self.life = self.max_life
        filename = f"{self.kind.capitalize()}_{self.color.capitalize()}.png"
        self.image = load_image(filename, fallback_rect_size=(48, 48))
        self.rect = self.image.get_rect(center=self.position)

    def hit(self, damage: int = 1):
        self.life -= damage
        if self.life < 0:
            self.life = 0

    @property
    def alive(self) -> bool:
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        surface.blit(self.image, self.rect)

    def draw_life_bar(self, surface: pygame.Surface):
        if not self.alive or self.max_life <= 0:
            return
        # petite barre de vie au-dessus de la pièce
        bar_width = self.rect.width
        bar_height = 5
        x = self.rect.left
        y = self.rect.top - bar_height - 2

        ratio = self.life / self.max_life
        filled_width = int(bar_width * ratio)

        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, filled_width, bar_height))
