import os
import pygame

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
PNG_DIR = os.path.join(ASSETS_DIR, "png")


def load_image(name: str, colorkey=None, fallback_rect_size=None, fallback_color=(200, 200, 200)):
    """Charge une image PNG depuis assets/png. Si introuvable, crée une surface colorée.

    name: nom de fichier, ex: "Pawn_white.png"
    fallback_rect_size: (w, h) pour une surface de secours.
    """
    path = os.path.join(PNG_DIR, name)
    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
        return image

    # Fallback: simple rectangle
    if fallback_rect_size is None:
        fallback_rect_size = (40, 40)
    surface = pygame.Surface(fallback_rect_size, pygame.SRCALPHA)
    surface.fill(fallback_color)
    return surface


def load_sound(name: str):
    sounds_dir = os.path.join(ASSETS_DIR, "sounds")
    path = os.path.join(sounds_dir, name)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None
    return None
