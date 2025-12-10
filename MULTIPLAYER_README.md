# Chess-Ping - Mode Multijoueur Réseau

## Description

Chess-Ping est un jeu hybride combinant des échecs et du ping-pong. Le mode multijoueur permet à deux joueurs de s'affronter en réseau via une architecture client-serveur TCP/IP.

## Architecture Réseau

### Protocole de Communication

Le jeu utilise des messages JSON sérialisés échangés via des sockets TCP Python. Les types de messages incluent :

- **Configuration initiale** : Envoyée par le serveur au client au début de la partie
- **Mises à jour de paddle** : Position Y des raquettes
- **Mises à jour de balle** : Position (x, y) et vélocité (vx, vy) 
- **Collisions avec pièces** : Vie restante des pièces touchées
- **Pièces détruites** : Notification de destruction
- **Scores** : Mise à jour des scores

### Autorité du Serveur

Le **serveur** a l'autorité sur :
- La physique de la balle
- La détection des collisions
- Les scores
- L'état du jeu

Le **client** :
- Contrôle son paddle
- Envoie ses positions de paddle au serveur
- Reçoit et affiche les mises à jour du serveur

## Modes de Jeu

### 1. Partie Locale
Jeu classique sur un seul PC avec deux joueurs côte à côte.

### 2. Créer une Partie (Serveur)
1. Sélectionner "Créer une partie (Serveur)" dans le menu principal
2. Le serveur démarre et affiche l'IP locale (ex: 192.168.1.100) et le port (5050)
3. Attendre qu'un client se connecte
4. Une fois connecté, configurer la partie :
   - Nombre de lignes du plateau (2, 4, 6, ou 8)
   - Types et nombre de pièces pour chaque camp
   - Qui commence avec le ballon
5. Le serveur contrôle le **paddle gauche** par défaut
6. Lancer la partie

**Contrôles serveur :**
- `W` / `S` : Déplacer le paddle gauche haut/bas
- Clic gauche ou `Espace` : Lancer la balle (au service)

### 3. Rejoindre une Partie (Client)
1. Sélectionner "Rejoindre une partie (Client)" dans le menu principal
2. Entrer l'adresse IP du serveur (fournie par l'hôte)
3. Entrer le port (par défaut 5050)
4. Cliquer sur "Se connecter"
5. Recevoir automatiquement la configuration de la partie
6. Le client contrôle le **paddle droit**
7. Attendre le lancement de la partie

**Contrôles client :**
- `↑` / `↓` : Déplacer le paddle droit haut/bas
- Clic gauche ou `Espace` : Lancer la balle (si c'est votre tour de servir)

## Test sur le Même PC (Localhost)

Pour tester le mode multijoueur sur un seul ordinateur :

### Méthode 1 : Deux fenêtres de terminal

**Terminal 1 - Serveur :**
```powershell
cd d:\mahasoa\ITU\S5\INFO301-ArchiLog\Chess-Ping
.\.venv\Scripts\Activate.ps1
python main.py
# Sélectionner "Créer une partie (Serveur)"
# Noter l'IP affichée (sera 127.0.0.1 ou votre IP locale)
```

**Terminal 2 - Client :**
```powershell
cd d:\mahasoa\ITU\S5\INFO301-ArchiLog\Chess-Ping
.\.venv\Scripts\Activate.ps1
python main.py
# Sélectionner "Rejoindre une partie (Client)"  
# Entrer IP: 127.0.0.1
# Entrer Port: 5050
```

### Méthode 2 : Script de lancement automatique

Créez un fichier `test_multiplayer.ps1` :

```powershell
# Lancer le serveur dans une nouvelle fenêtre
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python main.py"

# Attendre 2 secondes
Start-Sleep -Seconds 2

# Lancer le client dans une nouvelle fenêtre  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python main.py"
```

Puis exécutez :
```powershell
.\test_multiplayer.ps1
```

## Test sur Réseau Local (LAN)

### Configuration Serveur
1. Sur le PC serveur, lancez le jeu et sélectionnez "Créer une partie"
2. Notez l'IP locale affichée (ex: 192.168.1.100)
3. Assurez-vous que le port 5050 n'est pas bloqué par le pare-feu Windows

### Configuration Client  
1. Sur le PC client (même réseau local), lancez le jeu
2. Sélectionnez "Rejoindre une partie"
3. Entrez l'IP du serveur (ex: 192.168.1.100)
4. Entrez le port 5050
5. Cliquez sur "Se connecter"

### Déblocage du Pare-feu Windows

Si la connexion échoue, débloquez le port :

```powershell
# Exécuter en tant qu'Administrateur
New-NetFirewallRule -DisplayName "Chess-Ping Server" -Direction Inbound -Protocol TCP -LocalPort 5050 -Action Allow
```

## Dépannage

### Le client ne peut pas se connecter
- Vérifiez que le serveur est bien en attente de connexion
- Vérifiez l'adresse IP (utilisez `ipconfig` sur Windows)
- Vérifiez que le port 5050 n'est pas utilisé par une autre application
- Désactivez temporairement le pare-feu pour tester

### IP affichée est 127.0.0.1 mais vous voulez jouer en réseau
Le jeu affiche automatiquement votre IP locale. Si plusieurs interfaces réseau existent, utilisez :
```powershell
ipconfig
```
Et cherchez l'adresse IPv4 de votre adaptateur réseau actif.

### Lag ou décalage
- Le jeu envoie des mises à jour à chaque frame (60 FPS)
- Sur un réseau local, la latence devrait être < 5ms
- Sur Internet, la latence peut causer du décalage visible
- Assurez-vous que les deux machines ont une connexion stable

### Synchronisation des pièces
- Le serveur a l'autorité sur toutes les collisions
- Si une pièce semble avoir une vie différente entre serveur et client, c'est que la synchronisation a échoué
- Redémarrez la partie en cas de désynchronisation grave

## Architecture Technique

### Fichiers Réseau

- `game/net/connection.py` : Utilitaires de bas niveau pour l'envoi/réception de JSON
- `game/net/server.py` : Classe serveur TCP
- `game/net/client.py` : Classe client TCP  
- `game/net/protocol.py` : Définition des types de messages
- `game/network_engine.py` : Extension de GameEngine pour le mode réseau

### Flux de Communication

```
Serveur                          Client
   |                                |
   |--- MESSAGE CONFIG ------------>|
   |                                |
   |<-- PADDLE UPDATE (right) ------|
   |--- PADDLE UPDATE (left) ------>|
   |--- BALL UPDATE --------------->|
   |                                |
   |--- PIECE HIT ----------------->|
   |--- SCORE UPDATE -------------->|
   |                                |
   (boucle à ~60 FPS)
```

## Configuration Avancée

### Changer le Port par Défaut

Dans `game/net/server.py` et `game/net/client.py`, modifiez :
```python
def __init__(self, host: str = "0.0.0.0", port: int = 5050):
```

### Réduire l'Usage Réseau

Dans `game/network_engine.py`, augmentez l'intervalle :
```python
self.network_update_interval = 2  # Envoyer toutes les 2 frames au lieu de 1
```

### Logs de Débogage

Ajoutez des prints dans les fonctions `_send_as_server()` et `_recv_as_client()` pour voir les messages échangés.

## Améliorations Futures

- [ ] Choix du paddle pour l'hôte (gauche ou droit)
- [ ] Support de plus de 2 joueurs (mode spectateur)
- [ ] Reconnexion automatique en cas de déconnexion
- [ ] Compression des messages pour réduire la bande passante
- [ ] Prédiction côté client pour réduire le lag perçu
- [ ] Chat textuel entre joueurs
- [ ] Matchmaking avec serveur central
