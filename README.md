# Chess-Ping 🏓♟️

Chess-Ping est un jeu hybride combinant un **plateau d’échecs simplifié** et un **mini‑jeu de ping‑pong**.  
Deux joueurs s’affrontent en faisant rebondir une balle sur des raquettes (paddles) pour toucher et détruire les pièces adverses.

Le jeu propose :
- **Un mode local** (2 joueurs sur le même PC)  
- **Un mode multijoueur réseau** (architecture client‑serveur TCP/IP)

---

## 1. Prérequis

- **Système** : Windows (principalement testé sous Windows)
- **Python** : **Python 3.11** (ou 3.10+ au minimum)
- **Dépendances Python** :
  - `pygame`
  - (éventuelles autres dépendances listées dans `requirements.txt` si présent)

---

## 2. Installation

1. **Cloner le dépôt**

   ```bash
   git clone <URL_DU_DEPOT>
   cd Chess-Ping
   ```

2. **Installer les dépendances (sans environnement virtuel)**

   Depuis la racine du projet :

   ```bash
   pip install pygame
   ```

   ou, si un `requirements.txt` existe :

   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Lancer le jeu

Depuis la racine du projet :

```bash
python main.py
```

Le **menu principal** s’ouvre avec 3 options :
- `Partie locale`
- `Créer une partie (Serveur)`
- `Rejoindre une partie (Client)`

---

## 4. Modes de jeu et étapes

### 4.1. Mode local (2 joueurs sur le même PC)

1. Lancer le jeu :

   ```bash
   python main.py
   ```

2. Dans le menu principal, cliquer sur **« Partie locale »**.
3. Écran de **pré‑configuration** :
   - Choisir le **nombre de lignes du plateau** (2, 4, 6 ou 8).
   - Configurer les **types et quantités de pièces** pour chaque camp.
4. Écran de **choix du premier serveur** :
   - Choisir quel camp (gauche/droite) commence avec la balle.
5. La partie démarre :
   - Le plateau s’affiche.
   - Les paddles et la balle apparaissent.
   - La balle reste attachée au paddle du serveur jusqu’au premier lancement.

---

### 4.2. Mode multijoueur sur le même PC (localhost)

#### Côté Serveur (fenêtre 1)

1. Ouvrir un premier terminal dans le dossier du projet :

   ```bash
   cd Chess-Ping
   python main.py
   ```

2. Dans le menu, cliquer sur **« Créer une partie (Serveur) »**.
3. L’écran serveur affiche :
   - Un message « Serveur en attente de connexion… »
   - L’**IP locale** (souvent `127.0.0.1` ou une IP réseau)
   - Le **port** (par défaut `5050`)
4. Attendre qu’un client se connecte.
5. Une fois le client connecté :
   - Passer par la **pré‑configuration** (lignes, pièces, etc.).
   - Choisir le **premier serveur** (gauche/droite).
   - La partie démarre en mode serveur.

#### Côté Client (fenêtre 2)

1. Ouvrir un second terminal dans le dossier du projet :

   ```bash
   cd Chess-Ping
   python main.py
   ```

2. Cliquer sur **« Rejoindre une partie (Client) »**.
3. Entrer :
   - IP : `127.0.0.1`
   - Port : `5050`
4. Valider. Le client reçoit automatiquement la configuration.
5. Un écran de confirmation indique :
   - Le paddle contrôlé (gauche ou droite)
   - Le premier serveur
   - Appuyer sur une touche pour commencer.

---

### 4.3. Mode multijoueur sur réseau local (2 PC)

#### Côté Serveur (PC 1)

1. Sur le PC serveur, dans le dossier du projet :

   ```bash
   cd Chess-Ping
   python main.py
   ```

2. Cliquer sur **« Créer une partie (Serveur) »**.
3. Noter l’**IP locale** affichée (ex : `192.168.1.100`).
4. Vérifier que le **port 5050** n’est pas bloqué par le pare‑feu Windows.

#### Côté Client (PC 2)

1. Sur le PC client, dans le dossier du projet :

   ```bash
   cd Chess-Ping
   python main.py
   ```

2. Cliquer sur **« Rejoindre une partie (Client) »**.
3. Entrer :
   - IP : l’adresse du serveur (ex : `192.168.1.100`)
   - Port : `5050`
4. Valider et démarrer la partie après l’écran de confirmation.

#### Pare‑feu Windows (si nécessaire)

En PowerShell **en tant qu’administrateur** :

```powershell
New-NetFirewallRule -DisplayName "Chess-Ping Server" -Direction Inbound -Protocol TCP -LocalPort 5050 -Action Allow
```

---

## 5. Contrôles

| Rôle              | Paddle          | Monter      | Descendre    | Lancer la balle                     |
|-------------------|-----------------|-------------|--------------|-------------------------------------|
| Serveur (Hôte)    | Gauche (Rouge)  | `W`         | `S`          | `Espace` ou clic souris             |
| Client (Invité)   | Droit (Bleu)    | `↑`         | `↓`          | `Espace` ou clic (si au service)    |

- La **vitesse de la balle** est ajustable dans le HUD via des boutons `+` et `-`.
- Au service, l’**angle** de lancement dépend de la position de la souris.

---

## 6. Architecture du projet (aperçu)

- **Point d’entrée**
  - `main.py` : initialisation de Pygame, menu principal, sélection du mode de jeu et lancement de l’engine approprié.

- **Configuration**
  - `config.py` : constantes globales (taille de la fenêtre, plateau, couleurs, vitesses, etc.).

- **Moteurs de jeu**
  - `game/engine.py` : moteur principal (mode local), gestion du plateau + ping‑pong.
  - `game/network_engine.py` : extension réseau (synchronisation balle, paddles, pièces, scores).

- **Réseau**
  - `game/net/server.py` : serveur TCP `ChessPingServer`.
  - `game/net/client.py` : client TCP `ChessPingClient`.
  - `game/net/protocol.py` : définition et création des messages JSON (config, balle, paddles, score, pièces…).

- **Interface utilisateur**
  - `game/ui/main_menu.py` : menu principal (choix Local / Serveur / Client).
  - `game/ui/pre_game_config.py` : configuration du plateau et des pièces.
  - `game/ui/serve_choice.py` : choix du premier serveur (gauche/droite).
  - `game/ui/join_game.py` : écran de saisie IP/port pour le client.

- **Logique de jeu**
  - `game/chess/` : représentation du plateau, pièces, vies, affichage.
  - `game/pingpong/` : balle, paddles, collisions.

Pour plus de détails, voir :
- `QUICK_START.md` : guide de démarrage rapide multijoueur.
- `MULTIPLAYER_README.md` : documentation complète du mode réseau.
- `IMPLEMENTATION_SUMMARY.md` : résumé technique de l’implémentation.

---

## 7. Dépannage rapide

- **Le client ne se connecte pas**
  - Vérifier que le serveur est bien lancé et en attente.
  - Vérifier l’IP utilisée (commande `ipconfig`).
  - Vérifier que le port `5050` est ouvert (pare‑feu, autre application).

- **Le serveur reste “en attente de connexion”**
  - Vérifier l’IP saisie côté client.
  - Ouvrir le port `5050` dans le pare‑feu Windows (voir plus haut).

- **Désynchronisation du jeu (état différent entre client et serveur)**
  - Fermer les deux instances.
  - Relancer d’abord le serveur, puis le client.
  - Éviter une connexion réseau avec trop de latence.

---

## 8. Améliorations possibles

- Choix libre du paddle pour l’hôte (gauche ou droite).
- Support de spectateurs / plus de 2 joueurs.
- Reconnexion automatique en cas de déconnexion.
- Compression / limitation des messages réseau.
- Prédiction côté client pour réduire la latence perçue.
- Ajout d’un chat texte entre joueurs.

---
