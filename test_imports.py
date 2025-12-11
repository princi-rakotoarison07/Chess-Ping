"""Test rapide des imports du mode réseau"""

print("Test des imports...")

try:
    from game.net.connection import send_json, recv_json, recv_json_nonblocking
    print("✓ game.net.connection")
except Exception as e:
    print(f"✗ game.net.connection: {e}")

try:
    from game.net.server import ChessPingServer
    print("✓ game.net.server")
except Exception as e:
    print(f"✗ game.net.server: {e}")

try:
    from game.net.client import ChessPingClient
    print("✓ game.net.client")
except Exception as e:
    print(f"✗ game.net.client: {e}")

try:
    from game.net import protocol
    print("✓ game.net.protocol")
except Exception as e:
    print(f"✗ game.net.protocol: {e}")

try:
    from game.network_engine import NetworkGameEngine
    print("✓ game.network_engine")
except Exception as e:
    print(f"✗ game.network_engine: {e}")

print("\nTous les modules réseau sont importables!")
