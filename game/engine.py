from typing import List, Tuple

import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    LEFT_AREA_X,
    RIGHT_AREA_X,
    DEFAULT_FONT_NAME,
    BOARD_ROWS,
    BOARD_COLS,
)
from game.chess.board import ChessBoard
from game.chess.piece import Piece
from game.pingpong.ball import Ball
from game.pingpong.paddle import Paddle


class GameEngine:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(DEFAULT_FONT_NAME, 22)

        self.pieces_left, self.pieces_right = self._create_pieces()
        self.board = ChessBoard(self.pieces_left, self.pieces_right)
        self.ball = Ball()
        self.left_paddle, self.right_paddle = self._create_paddles()

        self.score_left = 0
        self.score_right = 0

    def _create_pieces(self) -> Tuple[List[Piece], List[Piece]]:
        pieces_left: List[Piece] = []
        pieces_right: List[Piece] = []

        # Placement classique des pièces sur la grille de l'échiquier
        # Lignes : 0 (noir pièces lourdes), 1 (pions noirs), 6 (pions blancs), 7 (blanc pièces lourdes)
        back_rank = [
            "rook",
            "knight",
            "bishop",
            "queen",
            "king",
            "bishop",
            "knight",
            "rook",
        ]

        # Pièces blanches (en bas du plateau)
        white_back_row = BOARD_ROWS - 1  # 7
        white_pawn_row = BOARD_ROWS - 2  # 6
        for col, kind in enumerate(back_rank):
            cx, cy = ChessBoard.get_square_center(white_back_row, col)
            piece = Piece(kind=kind, color="white", position=(cx, cy))
            piece.row = white_back_row
            piece.col = col
            pieces_left.append(piece)

        for col in range(BOARD_COLS):
            cx, cy = ChessBoard.get_square_center(white_pawn_row, col)
            piece = Piece(kind="pawn", color="white", position=(cx, cy))
            piece.row = white_pawn_row
            piece.col = col
            pieces_left.append(piece)

        # Pièces noires (en haut du plateau)
        black_back_row = 0
        black_pawn_row = 1
        for col, kind in enumerate(back_rank):
            cx, cy = ChessBoard.get_square_center(black_back_row, col)
            piece = Piece(kind=kind, color="dark", position=(cx, cy))
            piece.row = black_back_row
            piece.col = col
            pieces_right.append(piece)

        for col in range(BOARD_COLS):
            cx, cy = ChessBoard.get_square_center(black_pawn_row, col)
            piece = Piece(kind="pawn", color="dark", position=(cx, cy))
            piece.row = black_pawn_row
            piece.col = col
            pieces_right.append(piece)

        return pieces_left, pieces_right

    def _create_paddles(self):
        # Paddles devant les pièces
        left_x = LEFT_AREA_X + 60
        right_x = RIGHT_AREA_X - 60
        y = SCREEN_HEIGHT // 2 - 50

        left_paddle = Paddle(x=left_x, y=y, up_key=pygame.K_w, down_key=pygame.K_s)
        right_paddle = Paddle(x=right_x, y=y, up_key=pygame.K_UP, down_key=pygame.K_DOWN)
        return left_paddle, right_paddle

    def _handle_collisions(self):
        # collision balle / paddles
        if self.ball.rect.colliderect(self.left_paddle.rect):
            self.ball.vx = abs(self.ball.vx)
        if self.ball.rect.colliderect(self.right_paddle.rect):
            self.ball.vx = -abs(self.ball.vx)

        # collision balle / pièces
        damage = 1
        for piece in list(self.pieces_left):
            if piece.alive and self.ball.rect.colliderect(piece.rect):
                piece.hit(damage)
                self.ball.vx = abs(self.ball.vx)
                if not piece.alive:
                    self.pieces_left.remove(piece)
                    self.score_right += 1

        for piece in list(self.pieces_right):
            if piece.alive and self.ball.rect.colliderect(piece.rect):
                piece.hit(damage)
                self.ball.vx = -abs(self.ball.vx)
                if not piece.alive:
                    self.pieces_right.remove(piece)
                    self.score_left += 1

        # si la balle sort à gauche/droite, on remet au centre
        if self.ball.rect.right < 0:
            self.ball.reset()
            self.score_right += 1
        elif self.ball.rect.left > SCREEN_WIDTH:
            self.ball.reset()
            self.score_left += 1

    def _draw_hud(self):
        text = f"Pieces L:{len(self.pieces_left)}  R:{len(self.pieces_right)}  Score L:{self.score_left} R:{self.score_right}"
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(surface, (20, 20))

    def game_loop(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            # update
            self.left_paddle.update(keys)
            self.right_paddle.update(keys)
            self.ball.update()
            self._handle_collisions()

            # draw
            self.screen.fill((30, 30, 30))
            self.board.draw_board(self.screen)
            self.board.draw_pieces(self.screen)
            self.left_paddle.draw(self.screen)
            self.right_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self._draw_hud()

            pygame.display.flip()
