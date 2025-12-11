import pygame

# Fenêtre
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Plateau d'échecs (grille 8x8)
BOARD_ROWS = 2
BOARD_COLS = 8
CELL_SIZE = 80  # taille d'une case (modifiable)
BOARD_WIDTH = CELL_SIZE * BOARD_COLS
BOARD_HEIGHT = CELL_SIZE * BOARD_ROWS
BOARD_TOP = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
BOARD_LEFT = (SCREEN_WIDTH - BOARD_WIDTH) // 2

# Couleurs du damier
LIGHT_SQUARE_COLOR = (240, 217, 181)  # beige
DARK_SQUARE_COLOR = (181, 136, 99)    # marron

# Zones des pièces/paddles (pour le mini-jeu ping-pong)
LEFT_AREA_X = BOARD_LEFT - 200
RIGHT_AREA_X = BOARD_LEFT + BOARD_WIDTH + 200

# Paddles
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_SPEED = 6

# Balle
BALL_RADIUS = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = 4

# Vies des pièces par type
PIECE_LIFE = {
    "pawn": 1,
    "rook": 2,
    "knight": 2,
    "bishop": 2,
    "queen": 3,
    "king": 4,
}

# Police
pygame.font.init()
DEFAULT_FONT_NAME = pygame.font.get_default_font()
