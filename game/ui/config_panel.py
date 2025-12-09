import pygame
from typing import Dict, List, Callable
from utils.loader import load_image
from config import PIECE_LIFE


class ConfigPanel:
    """Panneau de configuration pour modifier les vies des pièces - Affichage horizontal."""
    
    def __init__(self, x: int, y: int, width: int, title: str, color_prefix: str):
        """
        Args:
            x, y: Position du panneau
            width: Largeur du panneau
            title: Titre du panneau ("Blancs" ou "Noirs")
            color_prefix: "white" ou "dark" pour charger les bonnes images
        """
        self.x = x
        self.y = y
        self.width = width
        self.title = title
        self.color_prefix = color_prefix
        
        # Types de pièces dans l'ordre d'affichage
        self.piece_types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        
        # Valeurs actuelles de configuration (copiées depuis PIECE_LIFE)
        self.piece_values: Dict[str, int] = PIECE_LIFE.copy()
        
        # Valeurs par défaut (pour le reset)
        self.default_values: Dict[str, int] = PIECE_LIFE.copy()
        
        # Champs input actifs
        self.input_values: Dict[str, str] = {k: str(v) for k, v in self.piece_values.items()}
        self.active_input: str = None  # Type de pièce dont l'input est actif
        
        # Charger les images des pièces
        self.piece_images: Dict[str, pygame.Surface] = {}
        for piece_type in self.piece_types:
            filename = f"{piece_type.capitalize()}_{self.color_prefix.capitalize()}.png"
            image = load_image(filename, fallback_rect_size=(35, 35))
            # Redimensionner à une taille uniforme pour l'affichage
            self.piece_images[piece_type] = pygame.transform.scale(image, (35, 35))
        
        # Dimensions horizontales
        self.piece_item_width = 100  # Largeur de chaque item de pièce
        self.padding = 8
        self.spacing = 5  # Espacement entre les éléments
        self.input_width = 45
        self.input_height = 25
        
        # Couleurs (fond transparent)
        self.bg_color = None  # Pas de fond
        self.title_color = (255, 255, 255)
        self.text_color = (220, 220, 220)
        self.input_bg_color = (40, 40, 50, 200)  # Semi-transparent
        self.input_active_color = (60, 100, 140, 220)
        self.button_color = (70, 130, 180, 200)
        self.button_hover_color = (100, 160, 210, 220)
        self.border_color = None  # Pas de bordure
        
        # Police
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 20)
        self.label_font = pygame.font.Font(None, 16)
        self.input_font = pygame.font.Font(None, 18)
        
        # Calcul de la hauteur totale
        self.total_height = 95  # Hauteur fixe pour le layout horizontal
        
        # Boutons (disposés horizontalement sous les pièces)
        self.button_height = 28
        button_total_width = self.piece_item_width * len(self.piece_types)
        button_width = (button_total_width - self.spacing * 2) // 3
        
        button_y = self.y + self.total_height - self.button_height - 5
        
        self.apply_button_rect = pygame.Rect(
            self.x,
            button_y,
            button_width,
            self.button_height
        )
        self.reset_button_rect = pygame.Rect(
            self.x + button_width + self.spacing,
            button_y,
            button_width,
            self.button_height
        )
        self.save_button_rect = pygame.Rect(
            self.x + button_width * 2 + self.spacing * 2,
            button_y,
            button_width,
            self.button_height
        )
        
        # Callbacks
        self.on_apply: Callable[[Dict[str, int]], None] = None
        self.on_reset: Callable[[], None] = None
        self.on_save: Callable[[Dict[str, int]], None] = None
        
        # État des boutons
        self.hovered_button = None
        
    def get_height(self) -> int:
        """Retourne la hauteur totale du panneau."""
        return self.total_height
    
    def get_input_rect(self, piece_type: str) -> pygame.Rect:
        """Retourne le rectangle du champ input pour un type de pièce (layout horizontal)."""
        idx = self.piece_types.index(piece_type)
        x = self.x + idx * self.piece_item_width + (self.piece_item_width - self.input_width) // 2
        y = self.y + 60  # Position fixe sous l'image et la vie
        return pygame.Rect(x, y, self.input_width, self.input_height)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Gère les événements pour le panneau.
        Retourne True si l'événement a été consommé.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Vérifier les clics sur les boutons
            if self.apply_button_rect.collidepoint(mouse_pos):
                self._apply_changes()
                return True
            elif self.reset_button_rect.collidepoint(mouse_pos):
                self._reset_values()
                return True
            elif self.save_button_rect.collidepoint(mouse_pos):
                self._save_config()
                return True
            
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
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            if self.apply_button_rect.collidepoint(mouse_pos):
                self.hovered_button = "apply"
            elif self.reset_button_rect.collidepoint(mouse_pos):
                self.hovered_button = "reset"
            elif self.save_button_rect.collidepoint(mouse_pos):
                self.hovered_button = "save"
            else:
                self.hovered_button = None
        
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
    
    def draw(self, surface: pygame.Surface):
        """Dessine le panneau de configuration."""
        panel_height = self.get_height()
        
        # Fond du panneau avec bordure
        panel_rect = pygame.Rect(self.x, self.y, self.width, panel_height)
        pygame.draw.rect(surface, self.bg_color, panel_rect)
        pygame.draw.rect(surface, self.border_color, panel_rect, 2)
        
        # Titre
        title_surface = self.title_font.render(self.title, True, self.title_color)
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, top=self.y + self.padding)
        surface.blit(title_surface, title_rect)
        
        # Ligne de séparation
        pygame.draw.line(
            surface,
            self.border_color,
            (self.x + self.padding, self.y + 35),
            (self.x + self.width - self.padding, self.y + 35),
            1
        )
        
        # Dessiner chaque item de pièce
        for idx, piece_type in enumerate(self.piece_types):
            item_y = self.y + 40 + idx * self.piece_item_height
            
            # Image de la pièce
            image = self.piece_images[piece_type]
            image_rect = image.get_rect(left=self.x + self.padding, centery=item_y + self.piece_item_height // 2 - 10)
            surface.blit(image, image_rect)
            
            # Vie actuelle
            life_text = f"Vie: {self.piece_values[piece_type]}"
            life_surface = self.label_font.render(life_text, True, self.text_color)
            life_rect = life_surface.get_rect(left=self.x + self.padding + 50, centery=item_y + self.piece_item_height // 2 - 10)
            surface.blit(life_surface, life_rect)
            
            # Champ input
            input_rect = self.get_input_rect(piece_type)
            is_active = (self.active_input == piece_type)
            input_color = self.input_active_color if is_active else self.input_bg_color
            
            pygame.draw.rect(surface, input_color, input_rect)
            pygame.draw.rect(surface, self.border_color, input_rect, 2 if is_active else 1)
            
            # Texte de l'input
            input_text = self.input_values[piece_type]
            if is_active:
                input_text += "|"  # Curseur clignotant
            
            input_surface = self.input_font.render(input_text, True, self.text_color)
            input_text_rect = input_surface.get_rect(center=input_rect.center)
            surface.blit(input_surface, input_text_rect)
        
        # Dessiner les boutons
        self._draw_button(surface, self.apply_button_rect, "Appliquer", "apply")
        self._draw_button(surface, self.reset_button_rect, "Réinitialiser", "reset")
        self._draw_button(surface, self.save_button_rect, "Sauvegarder", "save")
    
    def _draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str, button_id: str):
        """Dessine un bouton."""
        is_hovered = (self.hovered_button == button_id)
        color = self.button_hover_color if is_hovered else self.button_color
        
        pygame.draw.rect(surface, color, rect, border_radius=5)
        pygame.draw.rect(surface, self.border_color, rect, 2, border_radius=5)
        
        text_surface = self.label_font.render(text, True, self.title_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
