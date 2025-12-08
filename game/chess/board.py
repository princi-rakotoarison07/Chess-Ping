from typing import List

import pygame

from config import (
    BOARD_LEFT,
    BOARD_TOP,
    BOARD_ROWS,
    BOARD_COLS,
    CELL_SIZE,
    LIGHT_SQUARE_COLOR,
    DARK_SQUARE_COLOR,
)
from .piece import Piece


class ChessBoard:
    def __init__(self, pieces_left: List[Piece], pieces_right: List[Piece]):
        self.pieces_left = pieces_left
        self.pieces_right = pieces_right

    # --- Helpers grille ---
    @staticmethod
    def get_square_rect(row: int, col: int) -> pygame.Rect:
        """Rectangle de la case (row, col) en pixels."""
        x = BOARD_LEFT + col * CELL_SIZE
        y = BOARD_TOP + row * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    @staticmethod
    def get_square_center(row: int, col: int) -> tuple[int, int]:
        """Centre de la case (row, col) en pixels."""
        rect = ChessBoard.get_square_rect(row, col)
        return rect.center

    def draw_board(self, surface: pygame.Surface):
        # Dessin du damier 8x8 avec couleurs alternées
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
                rect = self.get_square_rect(row, col)
                pygame.draw.rect(surface, color, rect)

    def draw_pieces(self, surface: pygame.Surface):
        for p in self.pieces_left + self.pieces_right:
            p.draw(surface)
            p.draw_life_bar(surface)
