import pygame
from typing import Dict, Callable, List
from utils.loader import load_image
from config import PIECE_LIFE


class ConfigPanel:
    """Panneau de configuration horizontal et transparent pour modifier les vies des pièces."""
    
    def __init__(self, x: int, y: int, title: str, color_prefix: str, width: int | None = None):
        """
        Args:
            x, y: Position du panneau (coin supérieur gauche)
            title: Titre du panneau ("Blancs" ou "Noirs")
            color_prefix: "white" ou "dark" pour charger les bonnes images
        """
        self.x = x
        self.y = y
        self.title = title
        self.color_prefix = color_prefix
        self.width = width
        
        # Types de pièces dans l'ordre d'affichage (avec le roi)
        self.piece_types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        
        # Valeurs actuelles de configuration (copiées depuis PIECE_LIFE)
        self.piece_values: Dict[str, int] = PIECE_LIFE.copy()
        
        # Valeurs par défaut (pour le reset)
        self.default_values: Dict[str, int] = PIECE_LIFE.copy()
        
        # Champs input actifs
        self.input_values: Dict[str, str] = {k: str(v) for k, v in self.piece_values.items()}
        self.active_input: str = None  # Type de pièce dont l'input est actif
        
        # Liste des pièces du joueur (sera définie depuis l'extérieur)
        self.pieces_list: List = []
        
        # Charger les images des pièces
        self.piece_images: Dict[str, pygame.Surface] = {}
        for piece_type in self.piece_types:
            filename = f"{piece_type.capitalize()}_{self.color_prefix.capitalize()}.png"
            image = load_image(filename, fallback_rect_size=(40, 40))
            # Redimensionner à une taille agrandi pour l'affichage horizontal
            self.piece_images[piece_type] = pygame.transform.scale(image, (40, 40))
        
        # Dimensions pour layout horizontal (espace agrandi pour utiliser tout le footer)
        self.piece_item_width = 100  # Largeur de chaque colonne de pièce (très agrandi)
        self.piece_icon_size = 40
        self.padding = 15
        self.input_width = 60
        self.input_height = 28
        self.title_height = 30
        
        # Couleurs (fond transparent)
        self.title_color = (255, 255, 255)
        self.text_color = (220, 220, 220)
        self.input_bg_color = (40, 40, 50, 180)  # Semi-transparent
        self.input_active_color = (70, 70, 90, 200)
        self.border_color = (150, 150, 170)
        
        # Police
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 22)
        self.label_font = pygame.font.Font(None, 16)
        self.input_font = pygame.font.Font(None, 18)

        # Adapter dynamiquement la largeur des colonnes de pièces si une largeur fixe est fournie
        if self.width is not None:
            available_width = max(0, self.width - self.padding * 2)
            if self.piece_types:
                self.piece_item_width = max(60, available_width // len(self.piece_types))
                # Réduire légèrement la taille des icônes si nécessaire
                max_icon_size = int(self.piece_item_width * 0.8)
                if max_icon_size < self.piece_icon_size:
                    self.piece_icon_size = max(24, max_icon_size)
        
        # Callbacks
        self.on_apply: Callable[[Dict[str, int]], None] = None
        self.on_reset: Callable[[], None] = None
        self.on_save: Callable[[Dict[str, int]], None] = None
        
    def get_width(self) -> int:
        """Retourne la largeur totale du panneau."""
        if self.width is not None:
            return self.width
        return len(self.piece_types) * self.piece_item_width + self.padding * 2
    
    def get_height(self) -> int:
        """Retourne la hauteur totale du panneau."""
        return self.title_height + self.piece_icon_size + 25 + self.input_height + self.padding * 3
    
    def get_input_rect(self, piece_type: str) -> pygame.Rect:
        """Retourne le rectangle du champ input pour un type de pièce."""
        idx = self.piece_types.index(piece_type)
        x = self.x + self.padding + idx * self.piece_item_width + (self.piece_item_width - self.input_width) // 2
        y = self.y + self.title_height + self.piece_icon_size + 25 + self.padding
        return pygame.Rect(x, y, self.input_width, self.input_height)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Gère les événements pour le panneau.
        Retourne True si l'événement a été consommé.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Vérifier les clics sur les inputs
            for piece_type in self.piece_types:
                input_rect = self.get_input_rect(piece_type)
                if input_rect.collidepoint(mouse_pos):
                    self.active_input = piece_type
                    return True
            
            # Clic ailleurs = désactiver l'input
            self.active_input = None
            
        elif event.type == pygame.KEYDOWN:
            if self.active_input:
                if event.key == pygame.K_RETURN:
                    # Appliquer la valeur de l'input actif
                    self._apply_single_input(self.active_input)
                    self.active_input = None
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    # Effacer un caractère
                    self.input_values[self.active_input] = self.input_values[self.active_input][:-1]
                    return True
                elif event.key == pygame.K_ESCAPE:
                    # Annuler l'édition
                    self.input_values[self.active_input] = str(self.piece_values[self.active_input])
                    self.active_input = None
                    return True
                elif event.unicode.isdigit():
                    # Ajouter un chiffre
                    current = self.input_values[self.active_input]
                    if len(current) < 3:  # Limiter à 3 chiffres
                        self.input_values[self.active_input] += event.unicode
                    return True
        
        return False
    
    def _apply_single_input(self, piece_type: str):
        """Applique la valeur d'un seul input."""
        try:
            value = int(self.input_values[piece_type])
            if value > 0:
                self.piece_values[piece_type] = value
                if self.on_apply:
                    self.on_apply({piece_type: value})
        except ValueError:
            # Restaurer la valeur précédente si invalide
            self.input_values[piece_type] = str(self.piece_values[piece_type])
    
    def _apply_changes(self):
        """Applique toutes les modifications."""
        for piece_type in self.piece_types:
            try:
                value = int(self.input_values[piece_type])
                if value > 0:
                    self.piece_values[piece_type] = value
            except ValueError:
                self.input_values[piece_type] = str(self.piece_values[piece_type])
        
        if self.on_apply:
            self.on_apply(self.piece_values.copy())
    
    def _reset_values(self):
        """Réinitialise aux valeurs par défaut."""
        self.piece_values = self.default_values.copy()
        self.input_values = {k: str(v) for k, v in self.piece_values.items()}
        
        if self.on_reset:
            self.on_reset()
        
        if self.on_apply:
            self.on_apply(self.piece_values.copy())
    
    def _save_config(self):
        """Sauvegarde la configuration actuelle."""
        if self.on_save:
            self.on_save(self.piece_values.copy())
    
    def get_total_life_by_type(self, piece_type: str) -> int:
        """Calcule la somme totale des vies de toutes les pièces d'un type donné."""
        total = 0
        for piece in self.pieces_list:
            if piece.alive and piece.kind == piece_type:
                total += piece.life
        return total
    
    def draw(self, surface: pygame.Surface):
        """Dessine le panneau de configuration (fond transparent, layout horizontal)."""
        
        # Titre minimaliste (sans encadrement)
        title_surface = self.title_font.render(self.title, True, self.title_color)
        title_rect = title_surface.get_rect(centerx=self.x + self.get_width() // 2, top=self.y)
        surface.blit(title_surface, title_rect)
        
        # Dessiner chaque pièce en colonne horizontale
        for idx, piece_type in enumerate(self.piece_types):
            item_x = self.x + self.padding + idx * self.piece_item_width
            
            # Image de la pièce (centrée dans sa colonne)
            image = self.piece_images[piece_type]
            image_x = item_x + (self.piece_item_width - self.piece_icon_size) // 2
            image_y = self.y + self.title_height + self.padding
            surface.blit(image, (image_x, image_y))
            
            # Somme totale des vies de toutes les pièces de ce type (en dessous de l'icône)
            total_life = self.get_total_life_by_type(piece_type)
            life_text = f"{total_life}"
            life_surface = self.label_font.render(life_text, True, self.text_color)
            life_x = item_x + (self.piece_item_width - life_surface.get_width()) // 2
            life_y = image_y + self.piece_icon_size + 2
            surface.blit(life_surface, (life_x, life_y))
            
            # Champ input (en dessous du texte de vie)
            input_rect = self.get_input_rect(piece_type)
            is_active = (self.active_input == piece_type)
            
            # Créer une surface semi-transparente pour l'input
            input_surface_bg = pygame.Surface((input_rect.width, input_rect.height), pygame.SRCALPHA)
            input_color = self.input_active_color if is_active else self.input_bg_color
            input_surface_bg.fill(input_color)
            surface.blit(input_surface_bg, input_rect.topleft)
            
            # Bordure de l'input
            pygame.draw.rect(surface, self.border_color, input_rect, 2 if is_active else 1)
            
            # Texte de l'input
            input_text = self.input_values[piece_type]
            if is_active:
                input_text += "|"  # Curseur clignotant
            
            input_text_surface = self.input_font.render(input_text, True, self.text_color)
            input_text_rect = input_text_surface.get_rect(center=input_rect.center)
            surface.blit(input_text_surface, input_text_rect)
