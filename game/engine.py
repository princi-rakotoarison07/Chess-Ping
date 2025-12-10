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
    BALL_RADIUS,
    BALL_SPEED_X,
    BALL_SPEED_Y,
)
from game.chess.board import ChessBoard
from game.chess.piece import Piece
from game.pingpong.ball import Ball
from game.pingpong.paddle import Paddle
from game.ui.config_panel import ConfigPanel


class GameEngine:
    def __init__(self, screen: pygame.Surface, setup_config: Dict | None = None, first_server: str | None = None):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(DEFAULT_FONT_NAME, 22)

        self.setup_config = setup_config

        self.pieces_left, self.pieces_right = self._create_pieces()
        self.board = ChessBoard(self.pieces_left, self.pieces_right)
        self.ball = Ball()
        self.left_paddle, self.right_paddle = self._create_paddles()

        # Système de service manuel
        self.ball_attached = False
        self.serve_owner: str | None = None  # "white" (gauche) ou "dark" (droite)
        self.serve_dir = (1.0, 0.0)  # direction normale de tir
        if first_server in ("white", "dark"):
            self._start_serve(first_server)

        # Mémorise la dernière pièce touchée pour éviter plusieurs hits tant que la balle reste en contact
        self.last_hit_piece = None

        self.score_left = 0
        self.score_right = 0
        
        
        # Panneaux de configuration (footer) sur toute la largeur, sous le plateau
        panel_vertical_spacing = 10  # Espacement réduit pour une interface plus compacte

        from config import BOARD_TOP, BOARD_HEIGHT
        panels_y_position = BOARD_TOP + BOARD_HEIGHT + panel_vertical_spacing

        half_width = SCREEN_WIDTH // 2

        # Panneau pour les pièces BLANCHES (gauche) - moitié gauche de l'écran
        self.white_config_panel = ConfigPanel(
            x=0,
            y=panels_y_position,
            title="Blancs",
            color_prefix="white",
            width=half_width,
        )
        self.white_config_panel.pieces_list = self.pieces_left  # Pièces blanches
        self.white_config_panel.on_apply = lambda values: self._apply_config_white(values)
        self.white_config_panel.on_reset = lambda: self._reset_config_white()
        self.white_config_panel.on_save = lambda values: self._save_config("white", values)

        # Panneau pour les pièces NOIRES (droite) - moitié droite de l'écran
        self.dark_config_panel = ConfigPanel(
            x=half_width,
            y=panels_y_position,
            title="Noirs",
            color_prefix="dark",
            width=SCREEN_WIDTH - half_width,
        )
        self.dark_config_panel.pieces_list = self.pieces_right  # Pièces noires
        self.dark_config_panel.on_apply = lambda values: self._apply_config_dark(values)
        self.dark_config_panel.on_reset = lambda: self._reset_config_dark()
        self.dark_config_panel.on_save = lambda values: self._save_config("dark", values)

    def _create_pieces(self) -> Tuple[List[Piece], List[Piece]]:
        """Crée les pièces pour les deux camps.

        Si setup_config est fourni, on utilise les quantités et vies configurées
        en respectant la limite total_pieces <= 2 * BOARD_ROWS par couleur.
        Sinon, on pourrait rétablir un placement par défaut (non utilisé ici).
        """

        pieces_left: List[Piece] = []
        pieces_right: List[Piece] = []

        # Colonnes latérales pour le placement gauche/droite
        # Pour les blancs : col 0 = back-rank, col 1 = pions
        # Pour les noirs : col BOARD_COLS-1 = back-rank, col BOARD_COLS-2 = pions (miroir)
        left_cols = [0, 1]
        right_cols = [BOARD_COLS - 1, BOARD_COLS - 2]

        def add_pieces_for_color(color: str, cols: List[int], target_list: List[Piece]):
            """Place les pièces pour une couleur en suivant la configuration choisie.

            Logique stratégique :
            - Colonne "frontale" (cols[1]) : d'abord les tours, puis les pions,
              depuis la ligne la plus avancée vers l'arrière
              (bas -> haut pour les blancs, haut -> bas pour les noirs).
            - Colonne "arrière" (cols[0]) : roi puis reine, puis pièces mineures
              (fous, cavaliers) en partant de l'arrière vers l'avant.

            On ne crée jamais plus de pièces que ce qui est défini dans setup_config.
            """

            if not self.setup_config:
                return

            color_key = "white" if color == "white" else "dark"
            config_for_color = self.setup_config.get(color_key, {})

            # Compteurs restants par type, exactement ceux demandés par le joueur
            remaining: Dict[str, int] = {}
            for kind in ["rook", "queen", "king", "bishop", "knight", "pawn"]:
                data_kind = config_for_color.get(kind, {"count": 0})
                remaining[kind] = int(data_kind.get("count", 0))

            back_col, front_col = cols[0], cols[1]

            # Ordre des lignes selon la couleur
            if color == "white":
                # Blancs : front = lignes du bas vers le haut
                front_rows = list(range(BOARD_ROWS - 1, -1, -1))
                back_rows = list(range(BOARD_ROWS - 1, -1, -1))
            else:
                # Noirs : front = lignes du haut vers le bas (miroir)
                front_rows = list(range(BOARD_ROWS))
                back_rows = list(range(BOARD_ROWS))

            front_index = 0
            back_index = 0

            def place_piece(kind: str, row: int, col: int):
                cx, cy = ChessBoard.get_square_center(row, col)
                piece = Piece(kind=kind, color=color, position=(cx, cy))
                # Appliquer la vie configurée pour ce type de pièce
                data_kind = config_for_color.get(kind, {"life": piece.max_life})
                life_value = int(data_kind.get("life", piece.max_life))
                if life_value <= 0:
                    life_value = 1
                piece.max_life = life_value
                piece.life = life_value
                piece.row = row
                piece.col = col
                target_list.append(piece)

            # 1) Tours en colonne frontale
            while remaining.get("rook", 0) > 0 and front_index < len(front_rows):
                row = front_rows[front_index]
                front_index += 1
                remaining["rook"] -= 1
                place_piece("rook", row, front_col)

            # 2) Roi puis Reine en colonne arrière
            for kind in ["king", "queen"]:
                while remaining.get(kind, 0) > 0 and back_index < len(back_rows):
                    row = back_rows[back_index]
                    back_index += 1
                    remaining[kind] -= 1
                    place_piece(kind, row, back_col)

            # 3) Pièces mineures (fous, cavaliers) en colonne arrière
            for kind in ["bishop", "knight"]:
                while remaining.get(kind, 0) > 0 and back_index < len(back_rows):
                    row = back_rows[back_index]
                    back_index += 1
                    remaining[kind] -= 1
                    place_piece(kind, row, back_col)

            # 4) Pions restants en colonne frontale
            while remaining.get("pawn", 0) > 0 and front_index < len(front_rows):
                row = front_rows[front_index]
                front_index += 1
                remaining["pawn"] -= 1
                place_piece("pawn", row, front_col)

        add_pieces_for_color("white", left_cols, pieces_left)
        add_pieces_for_color("dark", right_cols, pieces_right)

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

    # --- Système de service / balle attachée ---

    def _start_serve(self, owner: str):
        """Attache la balle à la raquette du joueur donné et attend le lancement."""
        self.serve_owner = owner
        self.ball_attached = True
        self.ball.vx = 0
        self.ball.vy = 0

        # Positionner la balle au centre de la raquette, légèrement vers l'intérieur du plateau
        if owner == "white":
            paddle = self.left_paddle
            offset_x = BALL_RADIUS + 2
        else:
            paddle = self.right_paddle
            offset_x = -BALL_RADIUS - 2

        self.ball.x = paddle.rect.centerx + offset_x
        self.ball.y = paddle.rect.centery
        self.ball.rect.center = (self.ball.x, self.ball.y)

        # Direction initiale par défaut vers le centre du plateau
        if owner == "white":
            self.serve_dir = (1.0, 0.0)
        else:
            self.serve_dir = (-1.0, 0.0)

    def _update_serve_direction(self):
        """Met à jour la direction du service en fonction de la souris."""
        if not self.ball_attached:
            return

        mx, my = pygame.mouse.get_pos()
        dx = mx - self.ball.x
        dy = my - self.ball.y
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return
        length = max(1.0, length_sq ** 0.5)
        self.serve_dir = (dx / length, dy / length)

    def _launch_ball_if_requested(self, event: pygame.event.Event):
        """Lance la balle si le joueur clique ou appuie sur Espace/Entrée."""
        if not self.ball_attached:
            return

        launch = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            launch = True
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            launch = True

        if not launch:
            return

        dir_x, dir_y = self.serve_dir
        # Utiliser la norme de la vitesse de base de la balle
        base_speed = (BALL_SPEED_X ** 2 + BALL_SPEED_Y ** 2) ** 0.5
        if base_speed <= 0:
            base_speed = 1.0
        self.ball.vx = dir_x * base_speed
        self.ball.vy = dir_y * base_speed
        self.ball_attached = False

    def _draw_serve_arrow(self):
        """Dessine une flèche indiquant la direction du service quand la balle est attachée."""
        if not self.ball_attached:
            return

        dir_x, dir_y = self.serve_dir
        length = 40
        start = (int(self.ball.x), int(self.ball.y))
        end = (int(self.ball.x + dir_x * length), int(self.ball.y + dir_y * length))
        pygame.draw.line(self.screen, (255, 255, 0), start, end, 3)

    def _update_attached_ball_position(self):
        """Fait suivre la balle attachée à la raquette du serveur."""
        if not self.ball_attached or self.serve_owner not in ("white", "dark"):
            return
        if self.serve_owner == "white":
            paddle = self.left_paddle
            offset_x = BALL_RADIUS + 2
        else:
            paddle = self.right_paddle
            offset_x = -BALL_RADIUS - 2
        self.ball.x = paddle.rect.centerx + offset_x
        self.ball.y = paddle.rect.centery
        self.ball.rect.center = (self.ball.x, self.ball.y)

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
        # Si la balle est en attente de service, on ignore les collisions
        if self.ball_attached:
            return
        # collision balle / paddles
        # On utilise une zone de collision légèrement plus petite que le paddle
        # pour éviter les rebonds quand la balle est juste en dehors.
        shrink_y = BALL_RADIUS  # marge en haut et en bas
        left_coll_rect = self.left_paddle.rect.inflate(0, -2 * shrink_y)
        right_coll_rect = self.right_paddle.rect.inflate(0, -2 * shrink_y)

        if left_coll_rect.height > 0 and self.ball.rect.colliderect(left_coll_rect):
            self.ball.vx = abs(self.ball.vx)
            self.ball.color = (255, 0, 0)
        if right_coll_rect.height > 0 and self.ball.rect.colliderect(right_coll_rect):
            self.ball.vx = -abs(self.ball.vx)
            self.ball.color = (0, 0, 255)

        # Réinitialiser la dernière pièce touchée si la balle n'est plus en contact
        if self.last_hit_piece is not None:
            if (not self.last_hit_piece.alive) or (not self.ball.rect.colliderect(self.last_hit_piece.rect)):
                self.last_hit_piece = None

        # collision balle / pièces
        # Règle : une attaque de balle ne peut enlever qu'1 point de vie au total par frame.
        damage = 1
        hit_handled = False

        # On commence par tester les pièces de gauche
        for piece in list(self.pieces_left):
            if (
                not hit_handled
                and piece.alive
                and self.ball.rect.colliderect(piece.rect)
                and piece is not self.last_hit_piece
            ):
                before = piece.life
                piece.hit(damage)
                after = piece.life
                print(f"HIT LEFT {piece.color} {piece.kind}: {before} -> {after}")
                self.ball.vx = abs(self.ball.vx)
                if not piece.alive:
                    print(f"REMOVE LEFT {piece.color} {piece.kind} (life={after}), score_right={self.score_right + 1}")
                    self.pieces_left.remove(piece)
                    self.score_right += 1
                self.last_hit_piece = piece
                hit_handled = True
                break

        # Si aucune pièce de gauche n'a été touchée, on teste les pièces de droite
        if not hit_handled:
            for piece in list(self.pieces_right):
                if (
                    piece.alive
                    and self.ball.rect.colliderect(piece.rect)
                    and piece is not self.last_hit_piece
                ):
                    before = piece.life
                    piece.hit(damage)
                    after = piece.life
                    print(f"HIT RIGHT {piece.color} {piece.kind}: {before} -> {after}")
                    self.ball.vx = -abs(self.ball.vx)
                    if not piece.alive:
                        print(f"REMOVE RIGHT {piece.color} {piece.kind} (life={after}), score_left={self.score_left + 1}")
                        self.pieces_right.remove(piece)
                        self.score_left += 1
                    self.last_hit_piece = piece
                    break

        # La balle reste confinée dans le plateau : pas de reset basé sur les bords de la fenêtre

    def _draw_hud(self):
        text = f"Pieces L:{len(self.pieces_left)}  R:{len(self.pieces_right)}  Score L:{self.score_left} R:{self.score_right}"
        surface = self.font.render(text, True, (255, 255, 255))
        # Remonter le HUD pour réduire la hauteur du header
        self.screen.blit(surface, (20, 10))


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

                # Lancement manuel de la balle
                self._launch_ball_if_requested(event)

            keys = pygame.key.get_pressed()

            # update
            self.left_paddle.update(keys)
            self.right_paddle.update(keys)
            # Mise à jour du service (direction + position attachée)
            self._update_serve_direction()
            self._update_attached_ball_position()

            # Mettre à jour la balle uniquement si elle est libre
            if not self.ball_attached:
                self.ball.update()
            self._handle_collisions()

            # draw
            self.screen.fill((30, 30, 30))
            self.board.draw_board(self.screen)
            self.board.draw_pieces(self.screen)
            self.left_paddle.draw(self.screen)
            self.right_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self._draw_serve_arrow()
            self._draw_hud()

            # Dessiner un fond de footer semi-transparent sur toute la largeur
            footer_y = self.white_config_panel.y
            footer_height = self.white_config_panel.get_height()
            footer_surface = pygame.Surface((SCREEN_WIDTH, footer_height), pygame.SRCALPHA)
            footer_surface.fill((10, 10, 20, 180))
            self.screen.blit(footer_surface, (0, footer_y))

            # Dessiner les panneaux de configuration par-dessus le footer
            self.white_config_panel.draw(self.screen)
            self.dark_config_panel.draw(self.screen)

            pygame.display.flip()

