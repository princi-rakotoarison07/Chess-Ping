import pygame

import config
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from game.ui.main_menu import MainMenuScreen
from game.ui.pre_game_config import PreGameConfigScreen
from game.ui.serve_choice import ServeChoiceScreen
from game.ui.join_game import JoinGameScreen
from game.net.server import ChessPingServer
from game.net.client import ChessPingClient


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chess-Ping")

    # Menu principal : choix du mode de jeu
    menu = MainMenuScreen(screen)
    mode = menu.run()  # "local", "server", "client"

    if mode == "local":
        # Écran de pré-configuration: choix du nombre de lignes et des pièces
        pre_config_screen = PreGameConfigScreen(screen)
        setup = pre_config_screen.run()

        # Mettre à jour dynamiquement BOARD_ROWS et les valeurs dérivées
        config.BOARD_ROWS = setup["rows"]
        config.BOARD_HEIGHT = config.CELL_SIZE * config.BOARD_ROWS
        config.BOARD_TOP = (config.SCREEN_HEIGHT - config.BOARD_HEIGHT) // 2
        config.BOARD_WIDTH = config.CELL_SIZE * config.BOARD_COLS
        config.BOARD_LEFT = (config.SCREEN_WIDTH - config.BOARD_WIDTH) // 2
        config.LEFT_AREA_X = config.BOARD_LEFT - 200
        config.RIGHT_AREA_X = config.BOARD_LEFT + config.BOARD_WIDTH + 200

        # Écran de choix du premier serveur (gauche/droite)
        serve_choice_screen = ServeChoiceScreen(screen)
        first_server = serve_choice_screen.run()  # "left" pour Blancs, "right" pour Noirs

        # Importer GameEngine après la configuration du plateau pour qu'il lise les bons paramètres
        from game.engine import GameEngine

        engine = GameEngine(
            screen,
            setup_config=setup,
            first_server=first_server,
            net_role="local",
            net_socket=None,
        )
        engine.game_loop()

    elif mode == "server":
        # Mode serveur : démarrer un socket, afficher IP, attendre un client,
        # puis envoyer la configuration de partie.
        server = ChessPingServer()
        server.start_listening()

        local_ip = ChessPingServer.get_display_ip()
        font = pygame.font.Font(None, 32)
        info_lines = [
            "Serveur en attente de connexion...",
            f"IP locale : {local_ip}",
            f"Port : {server.port}",
            "Lancez le client sur l'autre machine et entrez cette IP.",
        ]

        waiting_client = True
        clock = pygame.time.Clock()
        while waiting_client:
            clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    server.close()
                    pygame.quit()
                    return

            screen.fill((10, 10, 30))
            for i, line in enumerate(info_lines):
                surf = font.render(line, True, (255, 255, 255))
                screen.blit(
                    surf,
                    surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + i * 30)),
                )
            pygame.display.flip()

            # Essayer d'accepter un client (blocant court)
            server.sock.settimeout(0.1)
            try:
                server.accept_client_blocking()
                waiting_client = False
            except Exception:
                continue

        # Une fois le client connecté, on fait la pré-config complète côté serveur
        pre_config_screen = PreGameConfigScreen(screen)
        setup = pre_config_screen.run()

        config.BOARD_ROWS = setup["rows"]
        config.BOARD_HEIGHT = config.CELL_SIZE * config.BOARD_ROWS
        config.BOARD_TOP = (config.SCREEN_HEIGHT - config.BOARD_HEIGHT) // 2
        config.BOARD_WIDTH = config.CELL_SIZE * config.BOARD_COLS
        config.BOARD_LEFT = (config.SCREEN_WIDTH - config.BOARD_WIDTH) // 2
        config.LEFT_AREA_X = config.BOARD_LEFT - 200
        config.RIGHT_AREA_X = config.BOARD_LEFT + config.BOARD_WIDTH + 200

        serve_choice_screen = ServeChoiceScreen(screen)
        first_server = serve_choice_screen.run()

        # Pour cette première version, on suppose que l'hôte joue le paddle gauche.
        host_paddle = "left"

        # Envoyer la configuration au client
        config_msg = {
            "type": "config",
            "setup": setup,
            "first_server": first_server,
            "host_paddle": host_paddle,
        }
        try:
            server.send_config(config_msg)
        except Exception:
            server.close()
            pygame.quit()
            return

        from game.engine import GameEngine

        engine = GameEngine(screen, setup_config=setup, first_server=first_server)
        try:
            engine.game_loop()
        finally:
            server.close()

    elif mode == "client":
        # Mode client : saisir IP/port, se connecter, recevoir la config,
        # l'afficher, puis (dans une étape suivante) lancer un client graphique.
        join_screen = JoinGameScreen(screen)
        ip_port = join_screen.run()
        if ip_port is None:
            pygame.quit()
            return
        ip, port = ip_port

        client = ChessPingClient(ip, port)
        try:
            client.connect()
            cfg = client.recv_config()
        except Exception:
            client.close()
            pygame.quit()
            return

        if cfg is None or cfg.get("type") != "config":
            client.close()
            pygame.quit()
            return

        # Appliquer la configuration reçue côté client
        setup = cfg.get("setup", {})
        first_server = cfg.get("first_server", "left")

        # Mettre à jour le plateau avec les mêmes paramètres que le serveur
        rows = setup.get("rows", config.BOARD_ROWS)
        config.BOARD_ROWS = rows
        config.BOARD_HEIGHT = config.CELL_SIZE * config.BOARD_ROWS
        config.BOARD_TOP = (config.SCREEN_HEIGHT - config.BOARD_HEIGHT) // 2
        config.BOARD_WIDTH = config.CELL_SIZE * config.BOARD_COLS
        config.BOARD_LEFT = (config.SCREEN_WIDTH - config.BOARD_WIDTH) // 2
        config.LEFT_AREA_X = config.BOARD_LEFT - 200
        config.RIGHT_AREA_X = config.BOARD_LEFT + config.BOARD_WIDTH + 200

        # Lancer GameEngine en mode client (spectateur synchronisé)
        from game.engine import GameEngine

        engine = GameEngine(
            screen,
            setup_config=setup,
            first_server=first_server,
            net_role="client",
            net_socket=client.sock,
        )

        try:
            engine.game_loop()
        finally:
            client.close()

    pygame.quit()


if __name__ == "__main__":
    main()
