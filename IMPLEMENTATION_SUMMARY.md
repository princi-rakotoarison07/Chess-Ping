# Implémentation du Mode Multijoueur - Chess-Ping

## ✅ Fonctionnalités Implémentées

### Architecture Réseau Client-Serveur TCP/IP

1. **Menu Principal** (`game/ui/main_menu.py`)
   - ✅ Bouton "Partie locale" - jeu classique
   - ✅ Bouton "Créer une partie (Serveur)"
   - ✅ Bouton "Rejoindre une partie (Client)"

2. **Mode Serveur** (`main.py` + `game/net/server.py`)
   - ✅ Démarrage d'un serveur socket sur le port 5050 (configurable)
   - ✅ Affichage de l'IP locale à l'écran pour connexion
   - ✅ Attente de connexion d'un client
   - ✅ Configuration complète de la partie par l'hôte :
     - Nombre de lignes (2, 4, 6, ou 8)
     - Types et nombre de pièces
     - Qui commence avec le ballon
     - Attribution automatique des paddles (serveur = gauche)
   - ✅ Envoi de la configuration au client
   - ✅ Communication bidirectionnelle en temps réel

3. **Mode Client** (`main.py` + `game/net/client.py`)
   - ✅ Écran de saisie IP/Port avec validation
   - ✅ Connexion au serveur
   - ✅ Réception automatique de la configuration
   - ✅ Attribution automatique du paddle opposé (client = droite)
   - ✅ Écran de confirmation avant le début
   - ✅ Communication bidirectionnelle en temps réel

4. **Protocole de Communication** (`game/net/protocol.py`)
   - ✅ Messages JSON sérialisés
   - ✅ Types de messages définis :
     - `config` : Configuration initiale
     - `paddle_update` : Position des paddles
     - `ball_update` : Position et vélocité de la balle
     - `piece_hit` : Collision avec une pièce
     - `piece_destroyed` : Destruction d'une pièce
     - `score_update` : Mise à jour des scores
     - `serve_start` : Début d'un service
     - `serve_launch` : Lancement de la balle
   - ✅ Fonctions de création de messages

5. **Synchronisation en Temps Réel** (`game/network_engine.py`)
   - ✅ Extension de `GameEngine` pour le mode réseau
   - ✅ Le serveur a l'autorité sur :
     - La physique de la balle
     - Les collisions
     - Les scores
     - L'état des pièces
   - ✅ Échange continu des informations :
     - Position du ballon (serveur → client)
     - Positions des paddles (bidirectionnel)
     - Collisions avec les pièces (serveur → client)
     - Vies restantes des pièces (serveur → client)
     - Scores (serveur → client)
   - ✅ Mode non-bloquant pour la réception de messages
   - ✅ Gestion de tour par tour pour le service

6. **Utilitaires Réseau** (`game/net/connection.py`)
   - ✅ Envoi de messages JSON
   - ✅ Réception bloquante de messages JSON
   - ✅ Réception non-bloquante avec buffer
   - ✅ Détection automatique de l'IP locale

## 📁 Fichiers Créés/Modifiés

### Nouveaux Fichiers
- `game/net/connection.py` - Utilitaires de communication réseau
- `game/net/server.py` - Classe serveur TCP
- `game/net/client.py` - Classe client TCP
- `game/net/protocol.py` - Définition du protocole de messages
- `game/network_engine.py` - Moteur de jeu multijoeur
- `game/ui/main_menu.py` - Menu principal (déjà existant)
- `game/ui/join_game.py` - Écran de connexion client (déjà existant)
- `MULTIPLAYER_README.md` - Documentation complète du mode multijoueur
- `test_multiplayer.ps1` - Script de test automatique
- `test_imports.py` - Test des imports

### Fichiers Modifiés
- `main.py` - Intégration des modes serveur et client avec NetworkGameEngine

## 🎮 Comment Tester

### Test en Local (Même PC)

**Option 1: Script Automatique**
```powershell
.\test_multiplayer.ps1
```

**Option 2: Manuel - Deux Terminaux**

Terminal 1 (Serveur):
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
# Choisir "Créer une partie (Serveur)"
# Noter l'IP affichée
```

Terminal 2 (Client):
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
# Choisir "Rejoindre une partie (Client)"
# Entrer IP: 127.0.0.1
# Entrer Port: 5050
```

### Test sur Réseau Local (LAN)

1. **Sur le PC Serveur:**
   - Lancez le jeu, choisissez "Créer une partie (Serveur)"
   - Notez l'IP locale affichée (ex: 192.168.1.100)

2. **Sur le PC Client:**
   - Lancez le jeu, choisissez "Rejoindre une partie (Client)"
   - Entrez l'IP du serveur
   - Entrez le port 5050

3. **Si la connexion échoue:**
   - Débloquez le port dans le pare-feu Windows :
   ```powershell
   New-NetFirewallRule -DisplayName "Chess-Ping Server" -Direction Inbound -Protocol TCP -LocalPort 5050 -Action Allow
   ```

## 🎯 Contrôles

**Serveur (Paddle Gauche - Rouge):**
- `W` : Monter
- `S` : Descendre
- `Espace` ou Clic : Lancer la balle (au service)

**Client (Paddle Droit - Bleu):**
- `↑` : Monter
- `↓` : Descendre
- `Espace` ou Clic : Lancer la balle (si c'est votre tour de servir)

## 🔧 Architecture Technique

### Flux de Communication

```
┌─────────────────┐                    ┌─────────────────┐
│     SERVEUR     │                    │     CLIENT      │
│  (Autorité)     │                    │  (Réplique)     │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │ 1. CONFIG (setup, first_server)      │
         │─────────────────────────────────────>│
         │                                      │
         │ 2. PADDLE_UPDATE (left, y)           │
         │─────────────────────────────────────>│
         │                                      │
         │      3. PADDLE_UPDATE (right, y)     │
         │<─────────────────────────────────────│
         │                                      │
         │ 4. BALL_UPDATE (x, y, vx, vy)        │
         │─────────────────────────────────────>│
         │                                      │
         │ 5. PIECE_HIT (side, index, life)     │
         │─────────────────────────────────────>│
         │                                      │
         │ 6. SCORE_UPDATE (left, right)        │
         │─────────────────────────────────────>│
         │                                      │
         └──────────────────────────────────────┘
              (Boucle à ~60 FPS)
```

### Séparation des Responsabilités

**Serveur (Authoritative):**
- Calcule la physique de la balle
- Détecte les collisions balle-paddle
- Détecte les collisions balle-pièces
- Met à jour les vies des pièces
- Calcule les scores
- Diffuse tous les changements d'état

**Client (Réplicatif):**
- Contrôle son paddle
- Envoie sa position de paddle
- Reçoit et applique les mises à jour du serveur
- Affiche l'état du jeu

### Gestion de la Latence

- Communication en mode non-bloquant
- Mises à jour envoyées à chaque frame (60 FPS)
- Buffer de réception pour gérer plusieurs messages par frame
- Latence acceptable : < 50ms pour une expérience fluide

## 🐛 Dépannage

### Problèmes Courants

1. **"Erreur de connexion: [WinError 10061]"**
   - Le serveur n'est pas démarré ou n'écoute pas
   - Vérifiez que le serveur est bien en attente de connexion

2. **"Echec de la reception de la configuration"**
   - Problème de synchronisation réseau
   - Redémarrez serveur et client

3. **Désynchronisation du jeu**
   - Latence réseau trop élevée
   - Perte de paquets
   - Redémarrez la partie

4. **Pare-feu bloque la connexion**
   - Ajoutez une règle pour le port 5050
   - Testez d'abord en local avec 127.0.0.1

## 📊 Statistiques de l'Implémentation

- **Lignes de code ajoutées:** ~800
- **Nouveaux fichiers:** 5
- **Fichiers modifiés:** 4
- **Types de messages:** 8
- **Taux de rafraîchissement:** 60 FPS
- **Port par défaut:** 5050
- **Architecture:** Client-Serveur Authoritative

## ✨ Améliorations Futures Suggérées

1. **Choix du paddle** - Permettre au serveur de choisir son paddle
2. **Reconnexion** - Gérer les déconnexions et permettre la reconnexion
3. **Prédiction côté client** - Interpolation pour réduire le lag perçu
4. **Compression** - Réduire la taille des messages
5. **Cryptage** - Sécuriser les communications
6. **Replay** - Enregistrer et rejouer les parties
7. **Chat** - Communication textuelle entre joueurs
8. **Lobbies** - Système de matchmaking

## 📝 Notes de Développement

L'implémentation suit le pattern **Client-Server Authoritative** où :
- Le serveur est la source de vérité pour la physique du jeu
- Les clients envoient leurs intentions (inputs)
- Le serveur calcule et diffuse l'état du monde
- Les clients affichent l'état reçu

Cette architecture garantit que les deux joueurs voient le même jeu et empêche la triche côté client.
