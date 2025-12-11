import socket
from typing import Any, Dict, List

from .connection import recv_json, recv_json_nonblocking, send_json


class ChessPingClient:
    """Client TCP simple pour Chess-Ping."""

    def __init__(self, host: str, port: int = 5050):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.recv_buffer = bytearray()

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def recv_config(self) -> Dict[str, Any] | None:
        if self.sock is None:
            raise RuntimeError("Client not connected")
        cfg = recv_json(self.sock)
        # Après réception de la config, passer en mode non-bloquant
        if self.sock:
            self.sock.setblocking(False)
        return cfg

    def send_game_message(self, message: Dict[str, Any]) -> bool:
        """Envoie un message de jeu au serveur. Retourne False si échec."""
        if self.sock is None:
            return False
        try:
            send_json(self.sock, message)
            return True
        except Exception:
            return False

    def recv_game_messages(self) -> List[Dict[str, Any]]:
        """Reçoit tous les messages de jeu disponibles (non-bloquant)."""
        if self.sock is None:
            return []
        return recv_json_nonblocking(self.sock, self.recv_buffer)

    def close(self) -> None:
        if self.sock is not None:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

