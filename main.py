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

        while True:
            engine = GameEngine(screen, setup_config=setup, first_server=first_server)
            result = engine.game_loop()
            if result != "replay":
                break


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
        from game.net import protocol
        # Pour l'instant, on envoie un multiplicateur de vitesse initial = 1.0.
        # Il sera ensuite synchronisé en temps réel si le serveur le modifie.
        config_msg = protocol.make_config_message(
            setup,
            first_server,
            host_paddle,
            ball_speed_factor=1.0,
        )
        
        try:
            server.send_config(config_msg)
        except Exception:
            server.close()
            pygame.quit()
            return

        # Utiliser NetworkGameEngine pour le mode multijoueur
        from game.network_engine import NetworkGameEngine

        try:
            while True:
                engine = NetworkGameEngine(
                    screen,
                    setup_config=setup,
                    first_server=first_server,
                    network_mode="server",
                    server_conn=server,
                    controlled_paddle=host_paddle,
                )
                result = engine.game_loop()
                if result != "replay":
                    break
        finally:
            server.close()


    elif mode == "client":
        # Mode client : saisir IP/port, se connecter, recevoir la config,
        # puis lancer le jeu en mode client.
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
        except Exception as e:
            # Afficher un message d'erreur
            font = pygame.font.Font(None, 32)
            screen.fill((10, 10, 30))
            msg = f"Erreur de connexion: {str(e)}"
            surf = font.render(msg, True, (255, 80, 80))
            screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            pygame.display.flip()
            pygame.time.wait(3000)
            client.close()
            pygame.quit()
            return

        if cfg is None:
            # Afficher un message d'erreur
            font = pygame.font.Font(None, 32)
            screen.fill((10, 10, 30))
            msg = "Echec de la reception de la configuration."
            surf = font.render(msg, True, (255, 80, 80))
            screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            pygame.display.flip()
            pygame.time.wait(3000)
            client.close()
            pygame.quit()
            return

        # Extraire la configuration
        setup = cfg.get("setup")
        first_server = cfg.get("first_server")
        host_paddle = cfg.get("host_paddle")
        ball_speed_factor = cfg.get("ball_speed_factor", 1.0)
        
        # Le client joue le paddle opposé à l'hôte
        client_paddle = "right" if host_paddle == "left" else "left"

        # Mettre à jour dynamiquement BOARD_ROWS et les valeurs dérivées
        config.BOARD_ROWS = setup["rows"]
        config.BOARD_HEIGHT = config.CELL_SIZE * config.BOARD_ROWS
        config.BOARD_TOP = (config.SCREEN_HEIGHT - config.BOARD_HEIGHT) // 2
        config.BOARD_WIDTH = config.CELL_SIZE * config.BOARD_COLS
        config.BOARD_LEFT = (config.SCREEN_WIDTH - config.BOARD_WIDTH) // 2
        config.LEFT_AREA_X = config.BOARD_LEFT - 200
        config.RIGHT_AREA_X = config.BOARD_LEFT + config.BOARD_WIDTH + 200

        # Afficher un écran de confirmation avant de lancer le jeu
        font = pygame.font.Font(None, 32)
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    client.close()
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

            screen.fill((10, 10, 30))
            lines = [
                "Connecté au serveur !",
                f"Vous contrôlez le paddle {client_paddle}",
                f"Premier serveur: {first_server}",
                "",
                "Appuyez sur une touche pour commencer...",
            ]
            for i, line in enumerate(lines):
                surf = font.render(line, True, (255, 255, 255))
                screen.blit(
                    surf,
                    surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + i * 35)),
                )

            pygame.display.flip()

        # Utiliser NetworkGameEngine pour le mode client
        from game.network_engine import NetworkGameEngine

        try:
            while True:
                engine = NetworkGameEngine(
                    screen,
                    setup_config=setup,
                    first_server=first_server,
                    network_mode="client",
                    client_conn=client,
                    controlled_paddle=client_paddle,
                )
                engine.ball_speed_factor = float(ball_speed_factor)
                result = engine.game_loop()
                if result != "replay":
                    break
        finally:
            client.close()


    pygame.quit()


if __name__ == "__main__":
    main()
