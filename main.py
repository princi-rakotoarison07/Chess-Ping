import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from game.engine import GameEngine


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chess-Ping")

    engine = GameEngine(screen)
    engine.game_loop()

    pygame.quit()


if __name__ == "__main__":
    main()
