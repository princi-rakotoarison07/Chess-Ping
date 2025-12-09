from typing import List, Tuple, Dict

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
    BOARD_LEFT,
    BOARD_WIDTH,
    CELL_SIZE,
    PADDLE_WIDTH,
)
from game.chess.board import ChessBoard
from game.chess.piece import Piece
from game.pingpong.ball import Ball
from game.pingpong.paddle import Paddle
from game.ui.config_panel import ConfigPanel


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
        
        
        # Panneaux de configuration (disposition horizontale sous le plateau)
        # Positionner les panneaux complètement en dehors du plateau d'échecs
        panel_vertical_spacing = 30  # Espacement entre le plateau et les panneaux
        
        # Calculer la position Y : sous le plateau (BOARD_TOP + BOARD_HEIGHT) + espacement
        from config import BOARD_TOP, BOARD_HEIGHT
        panels_y_position = BOARD_TOP + BOARD_HEIGHT + panel_vertical_spacing
        
        # Panneau pour les pièces NOIRES (gauche) - aligné sous le bord gauche du plateau
        self.dark_config_panel = ConfigPanel(
            x=BOARD_LEFT,
            y=panels_y_position,
            title="Noirs",
            color_prefix="dark"
        )
        self.dark_config_panel.pieces_list = self.pieces_right  # Pièces noires
        self.dark_config_panel.on_apply = lambda values: self._apply_config_dark(values)
        self.dark_config_panel.on_reset = lambda: self._reset_config_dark()
        self.dark_config_panel.on_save = lambda values: self._save_config("dark", values)
        
        # Panneau pour les pièces BLANCHES (droite) - aligné sous le bord droit du plateau
        # Calculer la position X pour aligner à droite du plateau
        dark_panel_width = self.dark_config_panel.get_width()
        self.white_config_panel = ConfigPanel(
            x=BOARD_LEFT + BOARD_WIDTH - dark_panel_width,
            y=panels_y_position,
            title="Blancs",
            color_prefix="white"
        )
        self.white_config_panel.pieces_list = self.pieces_left  # Pièces blanches
        self.white_config_panel.on_apply = lambda values: self._apply_config_white(values)
        self.white_config_panel.on_reset = lambda: self._reset_config_white()
        self.white_config_panel.on_save = lambda values: self._save_config("white", values)

    def _create_pieces(self) -> Tuple[List[Piece], List[Piece]]:
        pieces_left: List[Piece] = []
        pieces_right: List[Piece] = []

        # Placement latéral : colonnes 0-1 pour le joueur gauche, 6-7 pour le joueur droit
        # On utilise une rangée "forte" (back_rank) et une rangée de pions sur chaque camp.
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

        # Joueur gauche : colonnes 0 (pièces lourdes) et 1 (pions)
        left_back_col = 0
        left_pawn_col = 1
        for row, kind in enumerate(back_rank):
            cx, cy = ChessBoard.get_square_center(row, left_back_col)
            piece = Piece(kind=kind, color="white", position=(cx, cy))
            piece.row = row
            piece.col = left_back_col
            pieces_left.append(piece)

        for row in range(BOARD_ROWS):
            cx, cy = ChessBoard.get_square_center(row, left_pawn_col)
            piece = Piece(kind="pawn", color="white", position=(cx, cy))
            piece.row = row
            piece.col = left_pawn_col
            pieces_left.append(piece)

        # Joueur droit : colonnes 7 (pièces lourdes) et 6 (pions)
        right_back_col = BOARD_COLS - 1  # 7
        right_pawn_col = BOARD_COLS - 2  # 6
        for row, kind in enumerate(back_rank):
            cx, cy = ChessBoard.get_square_center(row, right_back_col)
            piece = Piece(kind=kind, color="dark", position=(cx, cy))
            piece.row = row
            piece.col = right_back_col
            pieces_right.append(piece)

        for row in range(BOARD_ROWS):
            cx, cy = ChessBoard.get_square_center(row, right_pawn_col)
            piece = Piece(kind="pawn", color="dark", position=(cx, cy))
            piece.row = row
            piece.col = right_pawn_col
            pieces_right.append(piece)

        return pieces_left, pieces_right

    def _create_paddles(self):
        # Paddles à l'intérieur du plateau, devant les pions :
        # - gauche : entre les colonnes 1 (pions blancs) et 2
        # - droite : entre les colonnes 5 et 6 (pions noirs)
        mid_row = BOARD_ROWS // 2

        # Colonnes de référence
        col1_rect = ChessBoard.get_square_rect(mid_row, 1)
        col2_rect = ChessBoard.get_square_rect(mid_row, 2)
        col5_rect = ChessBoard.get_square_rect(mid_row, 5)
        col6_rect = ChessBoard.get_square_rect(mid_row, 6)

        # Position X centrée entre les deux colonnes
        left_gap_center = (col1_rect.centerx + col2_rect.centerx) // 2
        right_gap_center = (col5_rect.centerx + col6_rect.centerx) // 2

        left_x = int(left_gap_center - PADDLE_WIDTH // 2)
        right_x = int(right_gap_center - PADDLE_WIDTH // 2)

        y = SCREEN_HEIGHT // 2 - 50

        # Rouge pour le joueur gauche, bleu pour le joueur droit
        left_paddle = Paddle(
            x=left_x,
            y=y,
            up_key=pygame.K_w,
            down_key=pygame.K_s,
            color=(255, 0, 0),
        )
        right_paddle = Paddle(
            x=right_x,
            y=y,
            up_key=pygame.K_UP,
            down_key=pygame.K_DOWN,
            color=(0, 0, 255),
        )
        return left_paddle, right_paddle

    def _apply_config_white(self, values: Dict[str, int]):
        """Applique la configuration des vies pour les pièces blanches."""
        for piece in self.pieces_left:
            if piece.kind in values:
                new_max_life = values[piece.kind]
                # Conserver le ratio de vie actuelle/max
                if piece.max_life > 0:
                    ratio = piece.life / piece.max_life
                    piece.max_life = new_max_life
                    piece.life = int(new_max_life * ratio)
                else:
                    piece.max_life = new_max_life
                    piece.life = new_max_life
    
    def _apply_config_dark(self, values: Dict[str, int]):
        """Applique la configuration des vies pour les pièces noires."""
        for piece in self.pieces_right:
            if piece.kind in values:
                new_max_life = values[piece.kind]
                # Conserver le ratio de vie actuelle/max
                if piece.max_life > 0:
                    ratio = piece.life / piece.max_life
                    piece.max_life = new_max_life
                    piece.life = int(new_max_life * ratio)
                else:
                    piece.max_life = new_max_life
                    piece.life = new_max_life
    
    def _reset_config_white(self):
        """Réinitialise les pièces blanches aux valeurs par défaut."""
        print("Configuration des pièces blanches réinitialisée")
    
    def _reset_config_dark(self):
        """Réinitialise les pièces noires aux valeurs par défaut."""
        print("Configuration des pièces noires réinitialisée")
    
    def _save_config(self, color: str, values: Dict[str, int]):
        """Sauvegarde la configuration actuelle."""
        import json
        try:
            # Charger les configurations existantes
            try:
                with open("chess_config.json", "r") as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {}
            
            # Mettre à jour la configuration pour la couleur donnée
            config[color] = values
            
            # Sauvegarder
            with open("chess_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"Configuration {color} sauvegardée avec succès!")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def _handle_collisions(self):
        # collision balle / paddles
        if self.ball.rect.colliderect(self.left_paddle.rect):
            self.ball.vx = abs(self.ball.vx)
            self.ball.color = (255, 0, 0)
        if self.ball.rect.colliderect(self.right_paddle.rect):
            self.ball.vx = -abs(self.ball.vx)
            self.ball.color = (0, 0, 255)

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

        # La balle reste confinée dans le plateau : pas de reset basé sur les bords de la fenêtre

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
                
                # Gérer les événements des panneaux de configuration
                self.white_config_panel.handle_event(event)
                self.dark_config_panel.handle_event(event)

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
            
            # Dessiner les panneaux de configuration
            self.white_config_panel.draw(self.screen)
            self.dark_config_panel.draw(self.screen)

            pygame.display.flip()

