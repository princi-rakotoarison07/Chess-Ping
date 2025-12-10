import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT


class MainMenuScreen:
    """Menu principal avec 3 options : Local / Serveur / Client.

    Retourne l'un des strings : "local", "server", "client".
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 56)
        self.button_font = pygame.font.Font(None, 32)

    def run(self) -> str:
        running = True
        choice: str | None = None

        btn_width = 320
        btn_height = 70
        spacing = 25

        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - (btn_height * 3 + spacing * 2) // 2

        rect_local = pygame.Rect(0, 0, btn_width, btn_height)
        rect_local.center = (center_x, start_y + btn_height // 2)

        rect_server = pygame.Rect(0, 0, btn_width, btn_height)
        rect_server.center = (center_x, rect_local.bottom + spacing + btn_height // 2)

        rect_client = pygame.Rect(0, 0, btn_width, btn_height)
        rect_client.center = (center_x, rect_server.bottom + spacing + btn_height // 2)

        while running:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if rect_local.collidepoint(event.pos):
                        choice = "local"
                        running = False
                    elif rect_server.collidepoint(event.pos):
                        choice = "server"
                        running = False
                    elif rect_client.collidepoint(event.pos):
                        choice = "client"
                        running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit

            self.screen.fill((20, 20, 40))

            title = self.title_font.render("Chess-Ping", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

            # Bouton Local
            self._draw_button(rect_local, "Partie locale")
            # Bouton Serveur
            self._draw_button(rect_server, "Créer une partie (Serveur)")
            # Bouton Client
            self._draw_button(rect_client, "Rejoindre une partie (Client)")

            pygame.display.flip()

        return choice or "local"

    def _draw_button(self, rect: pygame.Rect, text: str):
        pygame.draw.rect(self.screen, (60, 60, 120), rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 240), rect, 2, border_radius=10)
        label = self.button_font.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))
