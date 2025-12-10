import pygame

import config
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from game.ui.pre_game_config import PreGameConfigScreen
from game.ui.serve_choice import ServeChoiceScreen


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chess-Ping")

    # Écran de pré-configuration: choix du nombre de lignes et des pièces
    pre_config_screen = PreGameConfigScreen(screen)
    setup = pre_config_screen.run()

    # Mettre à jour dynamiquement BOARD_ROWS et les valeurs dérivées
    config.BOARD_ROWS = setup["rows"]
    config.BOARD_HEIGHT = config.CELL_SIZE * config.BOARD_ROWS
    config.BOARD_TOP = (config.SCREEN_HEIGHT - config.BOARD_HEIGHT) // 2
    config.BOARD_WIDTH = config.CELL_SIZE * config.BOARD_COLS
    config.BOARD_LEFT = (config.SCREEN_WIDTH - config.BOARD_WIDTH) // 2
    config.LEFT_AREA_X = config.BOARD_LEFT - 200
    config.RIGHT_AREA_X = config.BOARD_LEFT + config.BOARD_WIDTH + 200

    # Écran de choix du premier serveur (gauche/droite)
    serve_choice_screen = ServeChoiceScreen(screen)
    first_server = serve_choice_screen.run()  # "left" pour Blancs, "right" pour Noirs

    # Importer GameEngine après la configuration du plateau pour qu'il lise les bons paramètres
    from game.engine import GameEngine

    engine = GameEngine(screen, setup_config=setup, first_server=first_server)
    engine.game_loop()

    pygame.quit()


if __name__ == "__main__":
    main()
