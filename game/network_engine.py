"""GameEngine pour le mode multijoueur en réseau."""

from typing import Dict, Any, List
import math
import pygame

from game.engine import GameEngine
from game.net.server import ChessPingServer
from game.net.client import ChessPingClient
from game.net import protocol
from config import BALL_SPEED_X, BALL_SPEED_Y


class NetworkGameEngine(GameEngine):
    """Extension de GameEngine pour gérer le mode multijoueur en réseau.
    
    Le serveur a l'autorité sur la balle et les collisions.
    Les clients envoient leurs positions de paddle et reçoivent les mises à jour.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        setup_config: Dict | None = None,
        first_server: str = "left",
        network_mode: str = "server",  # "server" ou "client"
        server_conn: ChessPingServer | None = None,
        client_conn: ChessPingClient | None = None,
        controlled_paddle: str = "left",  # "left" ou "right"
    ):
        super().__init__(screen, setup_config, first_server)
        
        self.network_mode = network_mode
        self.server_conn = server_conn
        self.client_conn = client_conn
        self.controlled_paddle = controlled_paddle  # Quel paddle ce joueur contrôle
        
        # Compteur de frames pour limiter les mises à jour réseau
        self.network_update_counter = 0
        self.network_update_interval = 1  # Envoyer des updates toutes les N frames
        
        # Pour le serveur : suivi des indices de pièces pour la synchronisation
        self._build_piece_indices()
        
    def _build_piece_indices(self):
        """Construit des dictionnaires pour retrouver l'index d'une pièce."""
        self.piece_to_index_left = {id(piece): i for i, piece in enumerate(self.pieces_left)}
        self.piece_to_index_right = {id(piece): i for i, piece in enumerate(self.pieces_right)}

    def _send_network_update(self):
        """Envoie les mises à jour réseau appropriées."""
        if self.network_mode == "server" and self.server_conn:
            self._send_as_server()
        elif self.network_mode == "client" and self.client_conn:
            self._send_as_client()

    def _send_as_server(self):
        """Le serveur envoie la position de la balle et de son paddle."""
        if not self.server_conn:
            return
            
        # Envoyer la position de la balle (le serveur a l'autorité)
        ball_msg = protocol.make_ball_update_message(
            self.ball.x,
            self.ball.y,
            self.ball.vx,
            self.ball.vy,
            self.ball.color,
        )
        self.server_conn.send_game_message(ball_msg)
        
        # Envoyer la position du paddle du serveur
        if self.controlled_paddle == "left":
            paddle = self.left_paddle
        else:
            paddle = self.right_paddle
            
        paddle_msg = protocol.make_paddle_update_message(
            self.controlled_paddle, paddle.rect.y
        )
        self.server_conn.send_game_message(paddle_msg)

    def _send_as_client(self):
        """Le client envoie la position de son paddle."""
        if not self.client_conn:
            return
            
        if self.controlled_paddle == "left":
            paddle = self.left_paddle
        else:
            paddle = self.right_paddle
            
        paddle_msg = protocol.make_paddle_update_message(
            self.controlled_paddle, paddle.rect.y
        )
        self.client_conn.send_game_message(paddle_msg)

    def _recv_network_updates(self):
        """Reçoit et applique les mises à jour réseau."""
        if self.network_mode == "server" and self.server_conn:
            self._recv_as_server()
        elif self.network_mode == "client" and self.client_conn:
            self._recv_as_client()

    def _recv_as_server(self):
        """Le serveur reçoit les positions de paddle du client."""
        if not self.server_conn:
            return
            
        messages = self.server_conn.recv_game_messages()
        for msg in messages:
            msg_type = msg.get("type")
            
            if msg_type == protocol.MSG_PADDLE_UPDATE:
                # Mettre à jour le paddle du client
                side = msg.get("side")
                y = msg.get("y")
                if side == "left":
                    self.left_paddle.rect.y = y
                elif side == "right":
                    self.right_paddle.rect.y = y
                    
            elif msg_type == protocol.MSG_SERVE_LAUNCH:
                # Le client a décidé de lancer la balle (si c'est son tour de servir)
                # Pour l'instant, on laisse le serveur gérer le service
                pass

    def _recv_as_client(self):
        """Le client reçoit les mises à jour de la balle, du paddle adverse, etc."""
        if not self.client_conn:
            return
            
        messages = self.client_conn.recv_game_messages()
        for msg in messages:
            msg_type = msg.get("type")
            
            if msg_type == protocol.MSG_BALL_UPDATE:
                # Mettre à jour la position de la balle
                self.ball.x = msg.get("x", self.ball.x)
                self.ball.y = msg.get("y", self.ball.y)
                self.ball.vx = msg.get("vx", self.ball.vx)
                self.ball.vy = msg.get("vy", self.ball.vy)
                color = msg.get("color")
                if isinstance(color, (list, tuple)) and len(color) == 3:
                    self.ball.color = tuple(color)
                self.ball.rect.center = (int(self.ball.x), int(self.ball.y))
                # Si la balle se met en mouvement, on quitte l'état de service
                if self.serving and (self.ball.vx != 0 or self.ball.vy != 0):
                    self.serving = False
                
            elif msg_type == protocol.MSG_PADDLE_UPDATE:
                # Mettre à jour le paddle adverse
                side = msg.get("side")
                y = msg.get("y")
                if side == "left" and self.controlled_paddle != "left":
                    self.left_paddle.rect.y = y
                elif side == "right" and self.controlled_paddle != "right":
                    self.right_paddle.rect.y = y
                    
            elif msg_type == protocol.MSG_PIECE_HIT:
                # Une pièce a été touchée
                side = msg.get("side")
                piece_index = msg.get("piece_index")
                life = msg.get("life")
                
                pieces = self.pieces_left if side == "left" else self.pieces_right
                if 0 <= piece_index < len(pieces):
                    pieces[piece_index].life = life
                    
            elif msg_type == protocol.MSG_PIECE_DESTROYED:
                # Une pièce a été détruite
                side = msg.get("side")
                piece_index = msg.get("piece_index")
                
                pieces = self.pieces_left if side == "left" else self.pieces_right
                if 0 <= piece_index < len(pieces):
                    # alive est une propriété en lecture seule basée sur life>0.
                    # On marque donc la pièce comme morte en mettant sa vie à 0,
                    # puis on la retire de la liste locale pour rester aligné avec le serveur.
                    pieces[piece_index].life = 0
                    pieces.pop(piece_index)
                    
            elif msg_type == protocol.MSG_SCORE_UPDATE:
                # Mise à jour des scores
                self.score_left = msg.get("score_left", self.score_left)
                self.score_right = msg.get("score_right", self.score_right)
            elif msg_type == protocol.MSG_SPEED_UPDATE:
                # Synchronisation du multiplicateur de vitesse
                factor = msg.get("factor")
                if isinstance(factor, (int, float)):
                    self.ball_speed_factor = float(factor)
                    self._apply_ball_speed_factor()

    def _handle_collisions(self):
        """Override pour gérer les collisions différemment selon le mode réseau."""
        if self.network_mode == "server":
            # Le serveur calcule les collisions et les diffuse
            self._handle_collisions_server()
        else:
            # Le client ne calcule pas les collisions, il attend les updates du serveur
            pass

    def _handle_collisions_server(self):
        """Gestion des collisions côté serveur avec synchronisation réseau."""
        # Pendant le service, on ne gère pas les collisions (la balle est attachée)
        if self.serving:
            return

        # collision balle / paddles
        from config import BALL_RADIUS
        shrink_y = BALL_RADIUS
        left_coll_rect = self.left_paddle.rect.inflate(0, -2 * shrink_y)
        right_coll_rect = self.right_paddle.rect.inflate(0, -2 * shrink_y)

        if left_coll_rect.height > 0 and self.ball.rect.colliderect(left_coll_rect):
            self.ball.vx = abs(self.ball.vx)
            self.ball.color = (255, 0, 0)
        if right_coll_rect.height > 0 and self.ball.rect.colliderect(right_coll_rect):
            self.ball.vx = -abs(self.ball.vx)
            self.ball.color = (0, 0, 255)

        # Réinitialiser la dernière pièce touchée si la balle n'est plus en contact
        if self.last_hit_piece is not None:
            if (not self.last_hit_piece.alive) or (not self.ball.rect.colliderect(self.last_hit_piece.rect)):
                self.last_hit_piece = None

        # collision balle / pièces
        damage = 1
        hit_handled = False

        # Pièces de gauche
        for piece in list(self.pieces_left):
            if (
                not hit_handled
                and piece.alive
                and self.ball.rect.colliderect(piece.rect)
                and piece is not self.last_hit_piece
            ):
                before = piece.life
                piece.hit(damage)
                after = piece.life
                
                # Envoyer la mise à jour au client
                piece_index = self.piece_to_index_left.get(id(piece), -1)
                if piece_index >= 0 and self.server_conn:
                    hit_msg = protocol.make_piece_hit_message("left", piece_index, after)
                    self.server_conn.send_game_message(hit_msg)
                
                self.ball.vx = abs(self.ball.vx)
                
                if not piece.alive:
                    self.pieces_left.remove(piece)
                    self.score_right += 1
                    
                    # Envoyer la destruction et le score
                    if self.server_conn:
                        destroy_msg = protocol.make_piece_destroyed_message("left", piece_index)
                        self.server_conn.send_game_message(destroy_msg)
                        
                        score_msg = protocol.make_score_update_message(self.score_left, self.score_right)
                        self.server_conn.send_game_message(score_msg)
                    
                    # Reconstruire les indices
                    self._build_piece_indices()
                    
                self.last_hit_piece = piece
                hit_handled = True
                break

        # Pièces de droite
        if not hit_handled:
            for piece in list(self.pieces_right):
                if (
                    piece.alive
                    and self.ball.rect.colliderect(piece.rect)
                    and piece is not self.last_hit_piece
                ):
                    before = piece.life
                    piece.hit(damage)
                    after = piece.life
                    
                    # Envoyer la mise à jour au client
                    piece_index = self.piece_to_index_right.get(id(piece), -1)
                    if piece_index >= 0 and self.server_conn:
                        hit_msg = protocol.make_piece_hit_message("right", piece_index, after)
                        self.server_conn.send_game_message(hit_msg)
                    
                    self.ball.vx = -abs(self.ball.vx)
                    
                    if not piece.alive:
                        self.pieces_right.remove(piece)
                        self.score_left += 1
                        
                        # Envoyer la destruction et le score
                        if self.server_conn:
                            destroy_msg = protocol.make_piece_destroyed_message("right", piece_index)
                            self.server_conn.send_game_message(destroy_msg)
                            
                            score_msg = protocol.make_score_update_message(self.score_left, self.score_right)
                            self.server_conn.send_game_message(score_msg)
                        
                        # Reconstruire les indices
                        self._build_piece_indices()
                        
                    self.last_hit_piece = piece
                    break

    def game_loop(self):
        """Boucle de jeu avec intégration réseau."""
        running = True
        while running:
            self.clock.tick(60)  # FPS constant
            
            # Recevoir les mises à jour réseau
            self._recv_network_updates()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Gérer les événements des panneaux de configuration
                self.white_config_panel.handle_event(event)
                self.dark_config_panel.handle_event(event)

                # Gestion des boutons de vitesse de balle
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._speed_minus_rect.collidepoint(event.pos):
                        self.ball_speed_factor = max(self.ball_speed_min, self.ball_speed_factor - 0.1)
                        self._apply_ball_speed_factor()
                        # Synchroniser la nouvelle vitesse côté serveur
                        if self.network_mode == "server" and self.server_conn:
                            msg = protocol.make_speed_update_message(self.ball_speed_factor)
                            self.server_conn.send_game_message(msg)
                    elif self._speed_plus_rect.collidepoint(event.pos):
                        self.ball_speed_factor = min(self.ball_speed_max, self.ball_speed_factor + 0.1)
                        self._apply_ball_speed_factor()
                        # Synchroniser la nouvelle vitesse côté serveur
                        if self.network_mode == "server" and self.server_conn:
                            msg = protocol.make_speed_update_message(self.ball_speed_factor)
                            self.server_conn.send_game_message(msg)

                # Lancement manuel de la balle (seulement si c'est notre tour de servir)
                if self.serving:
                    can_serve = (
                        (self.server_side == self.controlled_paddle) or
                        (self.network_mode == "server")  # Le serveur a priorité
                    )
                    
                    if can_serve:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self._launch_ball()
                        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            self._launch_ball()

            keys = pygame.key.get_pressed()

            # Update du paddle contrôlé par ce joueur
            if self.controlled_paddle == "left":
                self.left_paddle.update(keys)
            else:
                self.right_paddle.update(keys)

            # Update de la physique (seulement côté serveur)
            if self.network_mode == "server":
                if self.serving:
                    self._update_serve()
                else:
                    self.ball.update()
                    self._handle_collisions()
            else:
                # Le client met à jour le service si c'est son paddle
                if self.serving and self.server_side == self.controlled_paddle:
                    self._update_serve()

            # Envoyer les mises à jour réseau périodiquement
            self.network_update_counter += 1
            if self.network_update_counter >= self.network_update_interval:
                self._send_network_update()
                self.network_update_counter = 0

            # Rendu (identique pour serveur et client)
            self.screen.fill((30, 30, 30))
            self.board.draw_board(self.screen)
            self.board.draw_pieces(self.screen)
            self.left_paddle.draw(self.screen)
            self.right_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self._draw_serve_arrow()
            self._draw_hud()

            # Dessiner un fond de footer semi-transparent sur toute la largeur
            from config import SCREEN_WIDTH
            footer_y = self.white_config_panel.y
            footer_height = self.white_config_panel.get_height()
            footer_surface = pygame.Surface((SCREEN_WIDTH, footer_height), pygame.SRCALPHA)
            footer_surface.fill((10, 10, 20, 180))
            self.screen.blit(footer_surface, (0, footer_y))

            # Dessiner les panneaux de configuration par-dessus le footer
            self.white_config_panel.draw(self.screen)
            self.dark_config_panel.draw(self.screen)

            pygame.display.flip()
