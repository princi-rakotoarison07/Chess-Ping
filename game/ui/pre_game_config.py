import pygame
from typing import Dict, Tuple

from config import SCREEN_WIDTH, SCREEN_HEIGHT, PIECE_LIFE
from utils.loader import load_image


PIECE_TYPES = ["pawn", "rook", "knight", "bishop", "queen", "king"]
ROW_OPTIONS = [2, 4, 6, 8]


class PreGameConfigScreen:
    """Écran de configuration avant le lancement de la partie.

    - Choix du nombre de lignes (BOARD_ROWS)
    - Choix des quantités et vies par type de pièce pour Blancs et Noirs
    - Limite: total des pièces par couleur <= 2 * BOARD_ROWS
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Valeurs par défaut
        self.selected_rows = 2

        # Structures: {color: {kind: {"count": int, "life": int}}}
        self.data: Dict[str, Dict[str, Dict[str, int]]] = {
            "white": {k: {"count": 0, "life": PIECE_LIFE.get(k, 1)} for k in PIECE_TYPES},
            "dark": {k: {"count": 0, "life": PIECE_LIFE.get(k, 1)} for k in PIECE_TYPES},
        }

        # Zone d'édition active: (color, kind, field) avec field in {"count", "life"}
        self.active_field: Tuple[str, str, str] | None = None

        # Police
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 24)
        self.input_font = pygame.font.Font(None, 22)

        # Chargement des images de pièces
        self.piece_images: Dict[Tuple[str, str], pygame.Surface] = {}
        for color in ("white", "dark"):
            for kind in PIECE_TYPES:
                filename = f"{kind.capitalize()}_{color.capitalize()}.png"
                img = load_image(filename, fallback_rect_size=(40, 40))
                img = pygame.transform.scale(img, (40, 40))
                self.piece_images[(color, kind)] = img

        self.warning_message: str | None = None

        # Initialiser avec une configuration par défaut pour 2 lignes
        self._reset_defaults_for_rows(self.selected_rows)

    # ---- Helpers de layout ----

    def _reset_defaults_for_rows(self, rows: int):
        """Réinitialise data avec une configuration par défaut complète
        en fonction du nombre de lignes choisi, sans dépasser 2 * rows pièces
        par couleur.

        Pour rows = 8, on obtient la configuration standard :
        8 pions, 2 tours, 2 cavaliers, 2 fous, 1 dame, 1 roi.
        Pour moins de lignes, on tronque en priorité : roi, dame, tours,
        fous, cavaliers, pions.
        """

        # Comptes standard d'un jeu d'échecs par couleur
        standard_counts = {
            "pawn": 8,
            "rook": 2,
            "knight": 2,
            "bishop": 2,
            "queen": 1,
            "king": 1,
        }

        limit = 2 * rows

        # Ordre de priorité pour garder les pièces les plus importantes
        # Tours en premier, puis reine, roi, puis pièces mineures
        priority_order = ["rook", "queen", "king", "bishop", "knight", "pawn"]

        def compute_counts() -> Dict[str, int]:
            remaining = limit
            counts: Dict[str, int] = {k: 0 for k in PIECE_TYPES}
            for kind in priority_order:
                if remaining <= 0:
                    break
                std = standard_counts.get(kind, 0)
                take = min(std, remaining)
                counts[kind] = take
                remaining -= take
            return counts

        base_counts = compute_counts()

        for color in ("white", "dark"):
            for kind in PIECE_TYPES:
                self.data[color][kind]["count"] = base_counts.get(kind, 0)
                # Vie par défaut issue de PIECE_LIFE
                self.data[color][kind]["life"] = PIECE_LIFE.get(kind, 1)

    def _get_rows_buttons_rects(self):
        buttons = []
        total_width = 4 * 80 + 3 * 20
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = 80
        for i, rows in enumerate(ROW_OPTIONS):
            x = start_x + i * (80 + 20)
            rect = pygame.Rect(x, y, 80, 40)
            buttons.append((rows, rect))
        return buttons

    def _get_piece_cell_rect(self, color: str, index: int, section_rect: pygame.Rect) -> pygame.Rect:
        # 6 types de pièces réparties horizontalement
        margin = 10
        available_width = section_rect.width - 2 * margin
        cell_width = available_width // len(PIECE_TYPES)
        x = section_rect.x + margin + index * cell_width
        y = section_rect.y + 10
        return pygame.Rect(x, y, cell_width, section_rect.height - 20)

    def _get_input_rects_for_piece(self, color: str, kind: str, index: int, section_rect: pygame.Rect):
        cell_rect = self._get_piece_cell_rect(color, index, section_rect)
        # image en haut, puis deux champs: count et life
        img_h = 40
        spacing = 5
        input_h = 26
        # zone pour inputs
        base_y = cell_rect.y + img_h + spacing + 18  # + label text height approximative
        # count en haut, life en bas
        input_w = cell_rect.width - 10
        x = cell_rect.x + 5
        count_rect = pygame.Rect(x, base_y, input_w, input_h)
        life_rect = pygame.Rect(x, base_y + input_h + spacing, input_w, input_h)
        return count_rect, life_rect

    def _handle_mouse_down(self, pos):
        # Boutons rows
        for rows, rect in self._get_rows_buttons_rects():
            if rect.collidepoint(pos):
                self.selected_rows = rows
                # Réappliquer une configuration par défaut complète
                self._reset_defaults_for_rows(rows)
                return

        # Zones de config pièces
        height_section = 260
        white_rect = pygame.Rect(0, SCREEN_HEIGHT - height_section, SCREEN_WIDTH // 2, height_section)
        dark_rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - height_section, SCREEN_WIDTH // 2, height_section)

        for color, section_rect in (("white", white_rect), ("dark", dark_rect)):
            for idx, kind in enumerate(PIECE_TYPES):
                count_rect, life_rect = self._get_input_rects_for_piece(color, kind, idx, section_rect)
                if count_rect.collidepoint(pos):
                    self.active_field = (color, kind, "count")
                    return
                if life_rect.collidepoint(pos):
                    self.active_field = (color, kind, "life")
                    return

        # Bouton Lancer
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - height_section - 70, 160, 40)
        if start_rect.collidepoint(pos):
            if self._validate():
                # Fin de l'écran
                self.running = False

    def _handle_key_down(self, event: pygame.event.Event):
        if event.key == pygame.K_ESCAPE:
            # ESC ferme la fenêtre Pygame complète
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        if not self.active_field:
            return
        color, kind, field = self.active_field
        current_str = str(self.data[color][kind][field])
        if event.key == pygame.K_BACKSPACE:
            current_str = current_str[:-1] if current_str else ""
        elif event.key == pygame.K_RETURN:
            # valider champ courant
            try:
                v = int(current_str)
                if v < 0:
                    v = 0
                self.data[color][kind][field] = v
            except ValueError:
                pass
            self.active_field = None
            return
        elif event.unicode.isdigit():
            if len(current_str) < 3:
                current_str += event.unicode
        else:
            return
        # Mettre à jour provisoirement
        try:
            self.data[color][kind][field] = int(current_str) if current_str else 0
        except ValueError:
            pass

    # ---- Validation ----

    def _validate(self) -> bool:
        max_pieces = 2 * self.selected_rows
        self.warning_message = None
        for color in ("white", "dark"):
            total = sum(self.data[color][k]["count"] for k in PIECE_TYPES)
            if total > max_pieces:
                self.warning_message = f"Trop de pieces pour {color} : {total} > {max_pieces}"
                return False
        # Au moins 1 pièce par couleur ? (optionnel mais plus intéressant)
        # On n'impose pas ici.
        return True

    # ---- Rendu ----

    def _draw_rows_selector(self):
        title = self.title_font.render("Configuration avant la partie", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=20))

        label = self.small_font.render("Choisir le nombre de lignes (BOARD_ROWS)", True, (220, 220, 220))
        self.screen.blit(label, label.get_rect(centerx=SCREEN_WIDTH // 2, y=55))

        for rows, rect in self._get_rows_buttons_rects():
            color_bg = (80, 80, 80) if rows != self.selected_rows else (120, 180, 120)
            pygame.draw.rect(self.screen, color_bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 2, border_radius=6)
            txt = self.small_font.render(str(rows), True, (0, 0, 0))
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        max_pieces = 2 * self.selected_rows
        info = self.small_font.render(f"Limite: total de pieces par couleur <= 2 x {self.selected_rows} = {max_pieces}", True, (230, 230, 150))
        self.screen.blit(info, info.get_rect(centerx=SCREEN_WIDTH // 2, y=140))

    def _draw_pieces_section(self):
        height_section = 260
        white_rect = pygame.Rect(0, SCREEN_HEIGHT - height_section, SCREEN_WIDTH // 2, height_section)
        dark_rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - height_section, SCREEN_WIDTH // 2, height_section)

        # titrés Blancs / Noirs
        for color, rect in (("white", white_rect), ("dark", dark_rect)):
            title = self.small_font.render("Blancs" if color == "white" else "Noirs", True, (255, 255, 255))
            self.screen.blit(title, (rect.x + 10, rect.y + 5))

        # Pièces et champs
        for color, rect in (("white", white_rect), ("dark", dark_rect)):
            for idx, kind in enumerate(PIECE_TYPES):
                cell_rect = self._get_piece_cell_rect(color, idx, rect)
                # image
                img = self.piece_images[(color, kind)]
                img_rect = img.get_rect(centerx=cell_rect.centerx, y=cell_rect.y + 25)
                self.screen.blit(img, img_rect)

                # label type
                lbl = self.small_font.render(kind.capitalize(), True, (220, 220, 220))
                lbl_rect = lbl.get_rect(centerx=cell_rect.centerx, y=cell_rect.y + 65)
                self.screen.blit(lbl, lbl_rect)

                # champs count & life
                count_rect, life_rect = self._get_input_rects_for_piece(color, kind, idx, rect)

                for field, r in (("count", count_rect), ("life", life_rect)):
                    is_active = self.active_field == (color, kind, field)
                    bg_color = (60, 60, 80) if not is_active else (90, 90, 130)
                    pygame.draw.rect(self.screen, bg_color, r, border_radius=4)
                    pygame.draw.rect(self.screen, (200, 200, 220), r, 1, border_radius=4)

                    value = str(self.data[color][kind][field])
                    txt = self.input_font.render(value, True, (255, 255, 255))
                    self.screen.blit(txt, txt.get_rect(center=r.center))


        # Bouton Lancer
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - height_section - 70, 160, 40)
        pygame.draw.rect(self.screen, (80, 150, 80), start_rect, border_radius=6)
        pygame.draw.rect(self.screen, (230, 230, 230), start_rect, 2, border_radius=6)
        label = self.small_font.render("Lancer la partie", True, (0, 0, 0))
        self.screen.blit(label, label.get_rect(center=start_rect.center))

        # Avertissement
        if self.warning_message:
            warn = self.small_font.render(self.warning_message, True, (255, 80, 80))
            self.screen.blit(warn, warn.get_rect(centerx=SCREEN_WIDTH // 2, y=start_rect.y - 30))

    # ---- Boucle principale ----

    def run(self) -> Dict:
        """Affiche l'écran jusqu'à validation, et retourne la configuration choisie."""
        self.running = True
        while self.running:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_mouse_down(event.pos)
                if event.type == pygame.KEYDOWN:
                    self._handle_key_down(event)

            self.screen.fill((20, 20, 40))
            self._draw_rows_selector()
            self._draw_pieces_section()

            pygame.display.flip()

        # On retourne une structure exploitable par le GameEngine / main
        return {
            "rows": self.selected_rows,
            "white": {k: self.data["white"][k].copy() for k in PIECE_TYPES},
            "dark": {k: self.data["dark"][k].copy() for k in PIECE_TYPES},
        }
