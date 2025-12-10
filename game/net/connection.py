import json
import socket
from typing import Any, Dict


ENCODING = "utf-8"


def send_json(sock: socket.socket, message: Dict[str, Any]) -> None:
    """Envoie un message JSON terminé par un '\n'."""
    data = json.dumps(message) + "\n"
    sock.sendall(data.encode(ENCODING))


def recv_json(sock: socket.socket) -> Dict[str, Any] | None:
    """Reçoit une ligne JSON depuis le socket. Bloquant, retourne None si fermé."""
    buffer = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        buffer += chunk
        if b"\n" in buffer:
            line, _, rest = buffer.partition(b"\n")
            # Si jamais plusieurs lignes arrivent, on ignore le reste pour l'instant
            try:
                return json.loads(line.decode(ENCODING))
            except json.JSONDecodeError:
                return None


def get_local_ip() -> str:
    """Retourne une IP locale utilisable (best effort)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
