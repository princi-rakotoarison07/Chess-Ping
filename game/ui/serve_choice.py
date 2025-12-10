import pygame
from typing import Literal

from config import SCREEN_WIDTH, SCREEN_HEIGHT


ServeSide = Literal["left", "right"]


class ServeChoiceScreen:
    """Écran simple pour choisir quel joueur commence (gauche/Blancs ou droite/Noirs)."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 40)
        self.label_font = pygame.font.Font(None, 28)

    def run(self) -> ServeSide:
        """Boucle jusqu'au choix de l'utilisateur, retourne "left" ou "right"."""
        running = True
        choice: ServeSide | None = None

        # Boutons
        btn_width = 220
        btn_height = 80
        spacing = 40
        total_width = btn_width * 2 + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT // 2

        left_rect = pygame.Rect(start_x, y, btn_width, btn_height)
        right_rect = pygame.Rect(start_x + btn_width + spacing, y, btn_width, btn_height)

        while running:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if left_rect.collidepoint(event.pos):
                        choice = "left"
                        running = False
                    elif right_rect.collidepoint(event.pos):
                        choice = "right"
                        running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        choice = "left"
                        running = False
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        choice = "right"
                        running = False

            self.screen.fill((15, 15, 30))

            title = self.title_font.render("Qui commence avec la balle ?", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))

            # Bouton gauche (Blancs)
            pygame.draw.rect(self.screen, (200, 200, 220), left_rect, border_radius=8)
            pygame.draw.rect(self.screen, (80, 80, 120), left_rect, 3, border_radius=8)
            txt_left = self.label_font.render("Blancs (gauche)", True, (0, 0, 0))
            self.screen.blit(txt_left, txt_left.get_rect(center=left_rect.center))

            # Bouton droite (Noirs)
            pygame.draw.rect(self.screen, (200, 200, 220), right_rect, border_radius=8)
            pygame.draw.rect(self.screen, (80, 80, 120), right_rect, 3, border_radius=8)
            txt_right = self.label_font.render("Noirs (droite)", True, (0, 0, 0))
            self.screen.blit(txt_right, txt_right.get_rect(center=right_rect.center))

            pygame.display.flip()

        return choice or "left"
