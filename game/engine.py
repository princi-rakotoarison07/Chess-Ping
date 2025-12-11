from typing import List, Tuple, Dict

import math
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
    def __init__(self, screen: pygame.Surface, setup_config: Dict | None = None, first_server: str = "left"):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(DEFAULT_FONT_NAME, 22)
        self.small_font = pygame.font.Font(DEFAULT_FONT_NAME, 18)

        self.setup_config = setup_config
        self.first_server = first_server  # "left" (Blancs) ou "right" (Noirs)

        self.pieces_left, self.pieces_right = self._create_pieces()
        self.board = ChessBoard(self.pieces_left, self.pieces_right)
        self.ball = Ball()
        self.left_paddle, self.right_paddle = self._create_paddles()

        # État de service : balle attachée au paddle jusqu'au lancement manuel
        self.serving = True
        self.server_side = self.first_server  # "left" ou "right"
        self.serve_angle = 0.0
        self._reset_ball_for_serve()

        # Configuration dynamique de la vitesse de balle
        self.ball_speed_factor = 1.0
        self.ball_speed_min = 0.5
        self.ball_speed_max = 2.0
        # Boutons +/- affichés dans le HUD (positions définies plus bas dans _draw_hud)
        self._speed_minus_rect = pygame.Rect(0, 0, 24, 24)
        self._speed_plus_rect = pygame.Rect(0, 0, 24, 24)

        # Boutons de gestion de partie (sauvegarder/charger/reset)
        self._save_button_rect = pygame.Rect(0, 0, 110, 26)
        self._load_button_rect = pygame.Rect(0, 0, 110, 26)
        self._reset_button_rect = pygame.Rect(0, 0, 110, 26)

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

    def _reset_ball_for_serve(self):
        """Positionne la balle attachée au paddle du serveur, sans mouvement."""
        if self.server_side == "right":
            paddle = self.right_paddle
            direction = -1
        else:
            paddle = self.left_paddle
            direction = 1

        # Balle légèrement devant le paddle
        if direction > 0:
            x = paddle.rect.right + BALL_RADIUS + 2
        else:
            x = paddle.rect.left - BALL_RADIUS - 2
        y = paddle.rect.centery

        self.ball.x = x
        self.ball.y = y
        self.ball.rect.center = (int(x), int(y))
        self.ball.vx = 0
        self.ball.vy = 0

        # Angle initial : vers l'adversaire
        self.serve_angle = 0.0 if direction > 0 else math.pi

    def _update_serve(self):
        """Met à jour la position de la balle et l'angle de service tant que l'on sert."""
        if not self.serving:
            return

        # Attacher la balle au paddle du serveur
        paddle = self.right_paddle if self.server_side == "right" else self.left_paddle
        direction = -1 if self.server_side == "right" else 1

        if direction > 0:
            x = paddle.rect.right + BALL_RADIUS + 2
        else:
            x = paddle.rect.left - BALL_RADIUS - 2
        y = paddle.rect.centery

        self.ball.x = x
        self.ball.y = y
        self.ball.rect.center = (int(x), int(y))

        # Calculer l'angle en fonction de la souris
        mx, my = pygame.mouse.get_pos()
        dx = mx - x
        dy = my - y
        if dx == 0 and dy == 0:
            # éviter un angle NaN
            self.serve_angle = 0.0 if direction > 0 else math.pi
        else:
            self.serve_angle = math.atan2(dy, dx)

    def _draw_serve_arrow(self):
        """Dessine une petite flèche indiquant la direction du service."""
        if not self.serving:
            return

        cx, cy = int(self.ball.x), int(self.ball.y)
        length = 50
        end_x = cx + int(math.cos(self.serve_angle) * length)
        end_y = cy + int(math.sin(self.serve_angle) * length)

        # Ligne principale
        pygame.draw.line(self.screen, (255, 255, 0), (cx, cy), (end_x, end_y), 2)

        # Petite pointe de flèche
        head_len = 10
        angle1 = self.serve_angle + math.radians(150)
        angle2 = self.serve_angle - math.radians(150)
        head1 = (
            end_x + int(math.cos(angle1) * head_len),
            end_y + int(math.sin(angle1) * head_len),
        )
        head2 = (
            end_x + int(math.cos(angle2) * head_len),
            end_y + int(math.sin(angle2) * head_len),
        )
        pygame.draw.line(self.screen, (255, 255, 0), (end_x, end_y), head1, 2)
        pygame.draw.line(self.screen, (255, 255, 0), (end_x, end_y), head2, 2)

    def _launch_ball(self):
        """Lance la balle dans la direction courante de la flèche."""
        if not self.serving:
            return
        base = math.hypot(BALL_SPEED_X, BALL_SPEED_Y)
        speed = base * self.ball_speed_factor
        self.ball.vx = math.cos(self.serve_angle) * speed
        self.ball.vy = math.sin(self.serve_angle) * speed
        self.serving = False

    def _apply_ball_speed_factor(self):
        """Réapplique le facteur de vitesse à la balle en mouvement."""
        if self.serving:
            # la vitesse sera appliquée au moment du service
            return
        # Si la balle est immobile, rien à faire
        if self.ball.vx == 0 and self.ball.vy == 0:
            return
        angle = math.atan2(self.ball.vy, self.ball.vx)
        base = math.hypot(BALL_SPEED_X, BALL_SPEED_Y)
        speed = base * self.ball_speed_factor
        self.ball.vx = math.cos(angle) * speed
        self.ball.vy = math.sin(angle) * speed

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
            """Place les pièces d'une couleur selon la taille du plateau.

            - Si BOARD_ROWS == 8 : placement classique d'échecs (back-rank + pions).
            - Si BOARD_ROWS < 8 : placement compact stratégique basé sur les nombres
              configurés (tours en avant, roi+reine derrière, puis autres pièces).
            """

            if not self.setup_config:
                return

            color_key = "white" if color == "white" else "dark"
            config_for_color = self.setup_config.get(color_key, {})

            back_col, front_col = cols[0], cols[1]

            # --- Cas 1 : plateau complet 8x8 -> placement standard ---
            if BOARD_ROWS == 8:
                # Compteurs restants par type (on respecte les quantités configurées)
                remaining: Dict[str, int] = {}
                for kind in ["rook", "knight", "bishop", "queen", "king", "pawn"]:
                    data_kind = config_for_color.get(kind, {"count": 0})
                    remaining[kind] = int(data_kind.get("count", 0))

                # Back-rank classique
                full_back_pattern = [
                    "rook",
                    "knight",
                    "bishop",
                    "queen",
                    "king",
                    "bishop",
                    "knight",
                    "rook",
                ]
                back_pattern = full_back_pattern[:BOARD_ROWS]

                # Back-rank : de haut en bas (rows 0..7) sur la colonne arrière
                for row, desired_kind in enumerate(back_pattern):
                    if remaining.get(desired_kind, 0) <= 0:
                        continue
                    remaining[desired_kind] -= 1
                    cx, cy = ChessBoard.get_square_center(row, back_col)
                    piece = Piece(kind=desired_kind, color=color, position=(cx, cy))

                    data_kind = config_for_color.get(desired_kind, {"life": piece.max_life})
                    life_value = int(data_kind.get("life", piece.max_life))
                    if life_value <= 0:
                        life_value = 1
                    piece.max_life = life_value
                    piece.life = life_value

                    piece.row = row
                    piece.col = back_col
                    target_list.append(piece)

                # Pions : sur la colonne avant, toutes les lignes
                pawn_remaining = remaining.get("pawn", 0)
                if pawn_remaining > 0:
                    for row in range(BOARD_ROWS):
                        if pawn_remaining <= 0:
                            break
                        cx, cy = ChessBoard.get_square_center(row, front_col)
                        piece = Piece(kind="pawn", color=color, position=(cx, cy))

                        data_kind = config_for_color.get("pawn", {"life": piece.max_life})
                        life_value = int(data_kind.get("life", piece.max_life))
                        if life_value <= 0:
                            life_value = 1
                        piece.max_life = life_value
                        piece.life = life_value

                        piece.row = row
                        piece.col = front_col
                        target_list.append(piece)

                return

            # --- Cas 2 : plateau réduit (2, 4, 6 lignes) -> placement stratégique ---

            # Compteurs restants par type (exactement ce que l'utilisateur a choisi)
            remaining: Dict[str, int] = {}
            for kind in ["rook", "queen", "king", "bishop", "knight", "pawn"]:
                data_kind = config_for_color.get(kind, {"count": 0})
                remaining[kind] = int(data_kind.get("count", 0))

            # Orientation des lignes :
            # - Blancs : du bas vers le haut
            # - Noirs : du haut vers le bas
            if color == "white":
                back_rows = list(range(BOARD_ROWS - 1, -1, -1))
                front_rows = list(range(BOARD_ROWS - 1, -1, -1))
            else:
                back_rows = list(range(0, BOARD_ROWS))
                front_rows = list(range(0, BOARD_ROWS))

            def create_piece(kind: str, row: int, col: int):
                cx, cy = ChessBoard.get_square_center(row, col)
                piece = Piece(kind=kind, color=color, position=(cx, cy))

                data_kind = config_for_color.get(kind, {"life": piece.max_life})
                life_value = int(data_kind.get("life", piece.max_life))
                if life_value <= 0:
                    life_value = 1
                piece.max_life = life_value
                piece.life = life_value

                piece.row = row
                piece.col = col
                target_list.append(piece)

            # 1) Tours en colonne avant (défense), en premier
            for row in front_rows:
                if remaining.get("rook", 0) <= 0:
                    break
                create_piece("rook", row, front_col)
                remaining["rook"] -= 1

            # 2) Roi puis Reine en colonne arrière
            for kind in ["king", "queen"]:
                for row in back_rows:
                    if remaining.get(kind, 0) <= 0:
                        break
                    occupied = any((p.row == row and p.col == back_col) for p in target_list)
                    if occupied:
                        continue
                    create_piece(kind, row, back_col)
                    remaining[kind] -= 1
                    break

            # 3) Autres pièces (fous, cavaliers, pions) remplissent les cases restantes
            other_order = ["bishop", "knight", "pawn"]

            # D'abord sur la colonne avant
            for kind in other_order:
                for row in front_rows:
                    if remaining.get(kind, 0) <= 0:
                        break
                    occupied = any((p.row == row and p.col == front_col) for p in target_list)
                    if occupied:
                        continue
                    create_piece(kind, row, front_col)
                    remaining[kind] -= 1

            # Puis sur la colonne arrière
            for kind in other_order:
                for row in back_rows:
                    if remaining.get(kind, 0) <= 0:
                        break
                    occupied = any((p.row == row and p.col == back_col) for p in target_list)
                    if occupied:
                        continue
                    create_piece(kind, row, back_col)
                    remaining[kind] -= 1

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
        # Pendant le service, on ne gère pas les collisions (la balle est attachée)
        if self.serving:
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
        # Infos de base (gauche)
        text = f"Pieces L:{len(self.pieces_left)}  R:{len(self.pieces_right)}  Score L:{self.score_left} R:{self.score_right}"
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(surface, (20, 10))

        # Contrôle de vitesse de balle (en haut à droite)
        speed_label = f"Vitesse: x{self.ball_speed_factor:.1f}"
        label_surf = self.font.render(speed_label, True, (255, 255, 255))
        padding = 10
        btn_size = 20
        spacing = 4

        # Largeur totale (texte + 2 boutons + espaces) pour rester à l'intérieur de l'écran
        total_width = label_surf.get_width() + spacing + btn_size + spacing + btn_size
        x = SCREEN_WIDTH - padding - total_width
        y = 10
        self.screen.blit(label_surf, (x, y))

        # Boutons - et + à droite du texte
        minus_x = x + label_surf.get_width() + spacing
        plus_x = minus_x + btn_size + spacing
        btn_y = y

        self._speed_minus_rect.update(minus_x, btn_y, btn_size, btn_size)
        self._speed_plus_rect.update(plus_x, btn_y, btn_size, btn_size)

        # Dessin des boutons
        pygame.draw.rect(self.screen, (60, 60, 90), self._speed_minus_rect)
        pygame.draw.rect(self.screen, (200, 200, 220), self._speed_minus_rect, 1)
        minus_txt = self.font.render("-", True, (255, 255, 255))
        self.screen.blit(minus_txt, minus_txt.get_rect(center=self._speed_minus_rect.center))

        pygame.draw.rect(self.screen, (60, 60, 90), self._speed_plus_rect)
        pygame.draw.rect(self.screen, (200, 200, 220), self._speed_plus_rect, 1)
        plus_txt = self.font.render("+", True, (255, 255, 255))
        self.screen.blit(plus_txt, plus_txt.get_rect(center=self._speed_plus_rect.center))
        # Boutons Sauver / Charger / Reset sous le score (zone en haut à gauche)
        buttons_y = 10 + surface.get_height() + 6
        btn_width = 95
        btn_height = 22
        btn_spacing = 10
        start_x = 20

        self._save_button_rect.update(start_x, buttons_y, btn_width, btn_height)
        self._load_button_rect.update(start_x + btn_width + btn_spacing, buttons_y, btn_width, btn_height)
        self._reset_button_rect.update(start_x + 2 * (btn_width + btn_spacing), buttons_y, btn_width, btn_height)

        for rect, label in [
            (self._save_button_rect, "save"),
            (self._load_button_rect, "charger"),
            #reinitialiser
            (self._reset_button_rect, "avereno"),
        ]:
            pygame.draw.rect(self.screen, (40, 40, 70), rect)
            pygame.draw.rect(self.screen, (200, 200, 220), rect, 1)
            txt = self.small_font.render(label, True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=rect.center))


    def _serialize_state(self) -> Dict:
        pieces_left_data = [
            {
                "kind": p.kind,
                "color": p.color,
                "row": p.row,
                "col": p.col,
                "life": p.life,
                "max_life": p.max_life,
            }
            for p in self.pieces_left
        ]
        pieces_right_data = [
            {
                "kind": p.kind,
                "color": p.color,
                "row": p.row,
                "col": p.col,
                "life": p.life,
                "max_life": p.max_life,
            }
            for p in self.pieces_right
        ]

        state = {
            "score_left": self.score_left,
            "score_right": self.score_right,
            "serving": self.serving,
            "server_side": self.server_side,
            "serve_angle": self.serve_angle,
            "ball_speed_factor": self.ball_speed_factor,
            "ball": {
                "x": self.ball.x,
                "y": self.ball.y,
                "vx": self.ball.vx,
                "vy": self.ball.vy,
                "color": list(self.ball.color),
            },
            "left_paddle_y": self.left_paddle.rect.y,
            "right_paddle_y": self.right_paddle.rect.y,
            "pieces_left": pieces_left_data,
            "pieces_right": pieces_right_data,
        }
        return state

    def _apply_state(self, state: Dict):
        from game.chess.board import ChessBoard
        from game.chess.piece import Piece

        pieces_left_data = state.get("pieces_left", [])
        pieces_right_data = state.get("pieces_right", [])

        new_pieces_left: List[Piece] = []
        new_pieces_right: List[Piece] = []

        for data in pieces_left_data:
            row = int(data.get("row", 0))
            col = int(data.get("col", 0))
            cx, cy = ChessBoard.get_square_center(row, col)
            piece = Piece(kind=data.get("kind"), color=data.get("color"), position=(cx, cy))
            piece.row = row
            piece.col = col
            piece.max_life = int(data.get("max_life", piece.max_life))
            piece.life = int(data.get("life", piece.max_life))
            new_pieces_left.append(piece)

        for data in pieces_right_data:
            row = int(data.get("row", 0))
            col = int(data.get("col", 0))
            cx, cy = ChessBoard.get_square_center(row, col)
            piece = Piece(kind=data.get("kind"), color=data.get("color"), position=(cx, cy))
            piece.row = row
            piece.col = col
            piece.max_life = int(data.get("max_life", piece.max_life))
            piece.life = int(data.get("life", piece.max_life))
            new_pieces_right.append(piece)

        self.pieces_left = new_pieces_left
        self.pieces_right = new_pieces_right
        self.board = ChessBoard(self.pieces_left, self.pieces_right)

        ball_data = state.get("ball", {})
        self.ball.x = float(ball_data.get("x", self.ball.x))
        self.ball.y = float(ball_data.get("y", self.ball.y))
        self.ball.vx = float(ball_data.get("vx", self.ball.vx))
        self.ball.vy = float(ball_data.get("vy", self.ball.vy))
        color = ball_data.get("color")
        if isinstance(color, (list, tuple)) and len(color) == 3:
            self.ball.color = tuple(color)
        self.ball.rect.center = (int(self.ball.x), int(self.ball.y))

        self.left_paddle.rect.y = int(state.get("left_paddle_y", self.left_paddle.rect.y))
        self.right_paddle.rect.y = int(state.get("right_paddle_y", self.right_paddle.rect.y))

        self.score_left = int(state.get("score_left", self.score_left))
        self.score_right = int(state.get("score_right", self.score_right))
        self.serving = bool(state.get("serving", self.serving))
        self.server_side = state.get("server_side", self.server_side)
        self.serve_angle = float(state.get("serve_angle", self.serve_angle))
        self.ball_speed_factor = float(state.get("ball_speed_factor", self.ball_speed_factor))
        self._apply_ball_speed_factor()

        self.last_hit_piece = None

        if hasattr(self, "_build_piece_indices"):
            try:
                self._build_piece_indices()
            except Exception:
                pass

    def _save_game_state(self, path: str = "game_state.json"):
        import json

        try:
            state = self._serialize_state()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            print(f"Etat de jeu sauvegarde dans {path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'etat de jeu: {e}")

    def _load_game_state(self, path: str = "game_state.json"):
        import json

        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            self._apply_state(state)
            print(f"Etat de jeu charge depuis {path}")
        except FileNotFoundError:
            print(f"Fichier de sauvegarde introuvable: {path}")
        except Exception as e:
            print(f"Erreur lors du chargement de l'etat de jeu: {e}")

    def _reset_game(self):
        from game.chess.board import ChessBoard
        from game.pingpong.ball import Ball

        self.pieces_left, self.pieces_right = self._create_pieces()
        self.board = ChessBoard(self.pieces_left, self.pieces_right)
        self.ball = Ball()
        self.left_paddle, self.right_paddle = self._create_paddles()

        self.score_left = 0
        self.score_right = 0
        self.serving = True
        self.server_side = self.first_server
        self.serve_angle = 0.0
        self._reset_ball_for_serve()
        self.ball_speed_factor = 1.0
        self._apply_ball_speed_factor()
        self.last_hit_piece = None

        if hasattr(self, "_build_piece_indices"):
            try:
                self._build_piece_indices()
            except Exception:
                pass

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

                # Gestion des boutons de vitesse de balle
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._speed_minus_rect.collidepoint(event.pos):
                        self.ball_speed_factor = max(self.ball_speed_min, self.ball_speed_factor - 0.1)
                        self._apply_ball_speed_factor()
                    elif self._speed_plus_rect.collidepoint(event.pos):
                        self.ball_speed_factor = min(self.ball_speed_max, self.ball_speed_factor + 0.1)
                        self._apply_ball_speed_factor()
                    elif self._save_button_rect.collidepoint(event.pos):
                        self._save_game_state()
                    elif self._load_button_rect.collidepoint(event.pos):
                        self._load_game_state()
                    elif self._reset_button_rect.collidepoint(event.pos):
                        self._reset_game()

                # Lancement manuel de la balle
                if self.serving:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._launch_ball()
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self._launch_ball()

            keys = pygame.key.get_pressed()

            # update
            self.left_paddle.update(keys)
            self.right_paddle.update(keys)
            if self.serving:
                self._update_serve()
            else:
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

