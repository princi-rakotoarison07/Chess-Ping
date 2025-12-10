import socket
from typing import Any, Dict

from .connection import recv_json


class ChessPingClient:
    """Client TCP simple pour Chess-Ping."""

    def __init__(self, host: str, port: int = 5050):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def recv_config(self) -> Dict[str, Any] | None:
        if self.sock is None:
            raise RuntimeError("Client not connected")
        return recv_json(self.sock)

    def close(self) -> None:
        if self.sock is not None:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
