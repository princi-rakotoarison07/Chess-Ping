import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT


class JoinGameScreen:
    """Écran pour saisir l'adresse IP et le port du serveur et se connecter."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 48)
        self.label_font = pygame.font.Font(None, 28)
        self.input_font = pygame.font.Font(None, 32)

        self.ip_text = "127.0.0.1"
        self.port_text = "5050"
        self.active_field = "ip"  # "ip" ou "port"

    def run(self) -> tuple[str, int] | None:
        ip_rect = pygame.Rect(0, 0, 260, 40)
        port_rect = pygame.Rect(0, 0, 120, 40)
        btn_rect = pygame.Rect(0, 0, 200, 50)

        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - 60

        ip_rect.center = (center_x, start_y)
        port_rect.center = (center_x, start_y + 60)
        btn_rect.center = (center_x, start_y + 130)

        running = True
        while running:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ip_rect.collidepoint(event.pos):
                        self.active_field = "ip"
                    elif port_rect.collidepoint(event.pos):
                        self.active_field = "port"
                    elif btn_rect.collidepoint(event.pos):
                        try:
                            port = int(self.port_text)
                            return self.ip_text, port
                        except ValueError:
                            pass
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_TAB:
                        self.active_field = "port" if self.active_field == "ip" else "ip"
                    elif event.key == pygame.K_RETURN:
                        try:
                            port = int(self.port_text)
                            return self.ip_text, port
                        except ValueError:
                            pass
                    else:
                        self._handle_text_input(event)

            self.screen.fill((15, 15, 35))

            title = self.title_font.render("Rejoindre une partie", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

            # IP
            self._draw_labeled_input("Adresse IP", self.ip_text, ip_rect, active=self.active_field == "ip")
            # Port
            self._draw_labeled_input("Port", self.port_text, port_rect, active=self.active_field == "port")

            # Bouton Se connecter
            pygame.draw.rect(self.screen, (60, 120, 60), btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, (200, 240, 200), btn_rect, 2, border_radius=8)
            txt = self.label_font.render("Se connecter", True, (0, 0, 0))
            self.screen.blit(txt, txt.get_rect(center=btn_rect.center))

            pygame.display.flip()

    def _handle_text_input(self, event: pygame.event.Event):
        if self.active_field == "ip":
            if event.key == pygame.K_BACKSPACE:
                self.ip_text = self.ip_text[:-1]
            elif event.unicode and (event.unicode.isdigit() or event.unicode == "."):
                if len(self.ip_text) < 30:
                    self.ip_text += event.unicode
        else:  # port
            if event.key == pygame.K_BACKSPACE:
                self.port_text = self.port_text[:-1]
            elif event.unicode and event.unicode.isdigit():
                if len(self.port_text) < 5:
                    self.port_text += event.unicode

    def _draw_labeled_input(self, label: str, value: str, rect: pygame.Rect, active: bool):
        label_surf = self.label_font.render(label, True, (220, 220, 220))
        self.screen.blit(label_surf, (rect.x, rect.y - 28))

        color_bg = (50, 50, 90) if not active else (70, 70, 130)
        pygame.draw.rect(self.screen, color_bg, rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 240), rect, 2, border_radius=6)

        text_surf = self.input_font.render(value, True, (255, 255, 255))
        self.screen.blit(text_surf, text_surf.get_rect(midleft=(rect.x + 10, rect.centery)))
