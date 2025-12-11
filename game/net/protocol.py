"""Protocole de communication pour Chess-Ping.

Définit les types de messages échangés entre le serveur et le client.
"""

from typing import Dict, Any, List, Tuple


# Types de messages
MSG_CONFIG = "config"
MSG_PADDLE_UPDATE = "paddle_update"
MSG_BALL_UPDATE = "ball_update"
MSG_SPEED_UPDATE = "speed_update"
MSG_PIECE_HIT = "piece_hit"
MSG_PIECE_DESTROYED = "piece_destroyed"
MSG_SCORE_UPDATE = "score_update"
MSG_SERVE_START = "serve_start"
MSG_SERVE_LAUNCH = "serve_launch"
MSG_GAME_END = "game_end"

# Requtes client -> serveur pour les actions de gestion de partie
MSG_REQ_SAVE = "req_save"
MSG_REQ_LOAD = "req_load"
MSG_REQ_RESET = "req_reset"

# Messages serveur -> client pour la synchronisation d'etat
MSG_GAME_STATE = "game_state"
MSG_RESET = "reset"
MSG_SAVE_CONFIRMED = "save_confirmed"


def make_config_message(
    setup: Dict,
    first_server: str,
    host_paddle: str,
    ball_speed_factor: float = 1.0,
) -> Dict[str, Any]:
    """Crée un message de configuration de partie.

    ball_speed_factor permet de synchroniser le multiplicateur de vitesse
    initial entre le serveur et le client.
    """
    return {
        "type": MSG_CONFIG,
        "setup": setup,
        "first_server": first_server,
        "host_paddle": host_paddle,
        "ball_speed_factor": ball_speed_factor,
    }


def make_paddle_update_message(side: str, y: float) -> Dict[str, Any]:
    """Crée un message de mise à jour de position de paddle.
    
    Args:
        side: "left" ou "right"
        y: Position Y du paddle
    """
    return {
        "type": MSG_PADDLE_UPDATE,
        "side": side,
        "y": y,
    }


def make_ball_update_message(x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int]) -> Dict[str, Any]:
    """Crée un message de mise à jour de la balle.

    La couleur est incluse pour que le client reflète les changements
    (par exemple après un rebond sur un paddle).
    """
    return {
        "type": MSG_BALL_UPDATE,
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy,
        "color": list(color),
    }


def make_speed_update_message(factor: float) -> Dict[str, Any]:
    """Crée un message de mise à jour du multiplicateur de vitesse de balle."""
    return {
        "type": MSG_SPEED_UPDATE,
        "factor": factor,
    }


def make_piece_hit_message(side: str, piece_index: int, life: int) -> Dict[str, Any]:
    """Crée un message indiquant qu'une pièce a été touchée.
    
    Args:
        side: "left" ou "right"
        piece_index: Index de la pièce dans la liste du côté
        life: Vie restante de la pièce
    """
    return {
        "type": MSG_PIECE_HIT,
        "side": side,
        "piece_index": piece_index,
        "life": life,
    }


def make_piece_destroyed_message(side: str, piece_index: int) -> Dict[str, Any]:
    """Crée un message indiquant qu'une pièce a été détruite.
    
    Args:
        side: "left" ou "right"
        piece_index: Index de la pièce dans la liste du côté
    """
    return {
        "type": MSG_PIECE_DESTROYED,
        "side": side,
        "piece_index": piece_index,
    }


def make_score_update_message(score_left: int, score_right: int) -> Dict[str, Any]:
    """Crée un message de mise à jour des scores."""
    return {
        "type": MSG_SCORE_UPDATE,
        "score_left": score_left,
        "score_right": score_right,
    }


def make_serve_start_message(server_side: str) -> Dict[str, Any]:
    """Crée un message indiquant le début d'un service.
    
    Args:
        server_side: "left" ou "right"
    """
    return {
        "type": MSG_SERVE_START,
        "server_side": server_side,
    }


def make_serve_launch_message(angle: float) -> Dict[str, Any]:
    """Crée un message indiquant le lancement de la balle lors du service.
    
    Args:
        angle: Angle de lancement en radians
    """
    return {
        "type": MSG_SERVE_LAUNCH,
        "angle": angle,
    }


def make_game_end_message(winner: str) -> Dict[str, Any]:
    """Crée un message indiquant la fin du jeu.
    
    Args:
        winner: "left" ou "right"
    """
    return {
        "type": MSG_GAME_END,
        "winner": winner,
    }


def make_req_save_message() -> Dict[str, Any]:
    return {"type": MSG_REQ_SAVE}


def make_req_load_message() -> Dict[str, Any]:
    return {"type": MSG_REQ_LOAD}


def make_req_reset_message() -> Dict[str, Any]:
    return {"type": MSG_REQ_RESET}


def make_game_state_message(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": MSG_GAME_STATE, "state": state}


def make_reset_message() -> Dict[str, Any]:
    return {"type": MSG_RESET}


def make_save_confirmed_message() -> Dict[str, Any]:
    return {"type": MSG_SAVE_CONFIRMED}
