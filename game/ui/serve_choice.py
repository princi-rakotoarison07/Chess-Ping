import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT


class ServeChoiceScreen:
    """Écran pour choisir quel joueur commence avec le ballon."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 40)
        self.button_font = pygame.font.Font(None, 32)

    def _get_buttons(self):
        width = 220
        height = 60
        spacing = 40
        total_width = width * 2 + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT // 2
        white_rect = pygame.Rect(start_x, y, width, height)
        dark_rect = pygame.Rect(start_x + width + spacing, y, width, height)
        return white_rect, dark_rect

    def run(self) -> str:
        """Affiche l'écran jusqu'à choix et retourne 'white' ou 'dark'."""
        choice = None
        while choice is None:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    white_rect, dark_rect = self._get_buttons()
                    if white_rect.collidepoint(event.pos):
                        choice = "white"
                    elif dark_rect.collidepoint(event.pos):
                        choice = "dark"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit

            self.screen.fill((15, 15, 30))

            title = self.title_font.render("Qui commence avec la balle ?", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 3))

            white_rect, dark_rect = self._get_buttons()

            # Bouton Blancs
            pygame.draw.rect(self.screen, (220, 220, 220), white_rect, border_radius=8)
            pygame.draw.rect(self.screen, (20, 20, 20), white_rect, 2, border_radius=8)
            txt_w = self.button_font.render("Blancs commencent", True, (0, 0, 0))
            self.screen.blit(txt_w, txt_w.get_rect(center=white_rect.center))

            # Bouton Noirs
            pygame.draw.rect(self.screen, (40, 40, 40), dark_rect, border_radius=8)
            pygame.draw.rect(self.screen, (220, 220, 220), dark_rect, 2, border_radius=8)
            txt_d = self.button_font.render("Noirs commencent", True, (255, 255, 255))
            self.screen.blit(txt_d, txt_d.get_rect(center=dark_rect.center))

            pygame.display.flip()

        return choice
