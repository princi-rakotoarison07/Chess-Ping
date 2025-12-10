import json
import socket
from typing import Any, Dict, List


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


def recv_json_nonblocking(sock: socket.socket, buffer: bytearray) -> List[Dict[str, Any]]:
    """Reçoit des messages JSON en mode non-bloquant.
    
    Args:
        sock: Socket à lire
        buffer: Buffer partagé pour accumuler les données
        
    Returns:
        Liste de messages JSON décodés (peut être vide)
    """
    messages = []
    
    try:
        # Recevoir les données disponibles
        chunk = sock.recv(4096)
        if chunk:
            buffer.extend(chunk)
    except BlockingIOError:
        # Pas de données disponibles, c'est normal en mode non-bloquant
        pass
    except Exception:
        # Erreur de connexion
        return messages
    
    # Traiter tous les messages complets dans le buffer
    while b"\n" in buffer:
        line, _, rest = buffer.partition(b"\n")
        buffer[:] = rest  # Modifier le buffer en place
        
        try:
            msg = json.loads(line.decode(ENCODING))
            messages.append(msg)
        except json.JSONDecodeError:
            # Message malformé, on l'ignore
            pass
    
    return messages


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
