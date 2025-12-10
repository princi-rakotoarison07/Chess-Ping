import socket
from typing import Any, Dict, List

from .connection import send_json, recv_json_nonblocking, get_local_ip


class ChessPingServer:
    """Serveur TCP simple pour Chess-Ping.

    Gère une seule connexion client pour l'instant.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5050):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.client_sock: socket.socket | None = None
        self.client_addr: tuple[str, int] | None = None
        self.recv_buffer = bytearray()

    def start_listening(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

    def accept_client_blocking(self) -> None:
        if self.sock is None:
            raise RuntimeError("Server socket not started. Call start_listening() first.")
        self.client_sock, self.client_addr = self.sock.accept()
        # Mettre le socket client en mode non-bloquant pour le jeu
        if self.client_sock:
            self.client_sock.setblocking(False)

    def send_config(self, config_msg: Dict[str, Any]) -> None:
        if self.client_sock is None:
            raise RuntimeError("No client connected")
        send_json(self.client_sock, config_msg)

    def send_game_message(self, message: Dict[str, Any]) -> bool:
        """Envoie un message de jeu au client. Retourne False si échec."""
        if self.client_sock is None:
            return False
        try:
            send_json(self.client_sock, message)
            return True
        except Exception:
            return False

    def recv_game_messages(self) -> List[Dict[str, Any]]:
        """Reçoit tous les messages de jeu disponibles (non-bloquant)."""
        if self.client_sock is None:
            return []
        return recv_json_nonblocking(self.client_sock, self.recv_buffer)

    def close(self) -> None:
        if self.client_sock is not None:
            try:
                self.client_sock.close()
            except Exception:
                pass
            self.client_sock = None
        if self.sock is not None:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    @staticmethod
    def get_display_ip() -> str:
        return get_local_ip()

