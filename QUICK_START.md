# 🎮 Chess-Ping - Guide de Démarrage Rapide Multijoueur

## ⚡ Test Rapide en 30 Secondes

### Sur le Même PC (Localhost)

1. **Ouvrez deux terminaux PowerShell**

2. **Terminal 1 - Serveur:**
```powershell
cd d:\mahasoa\ITU\S5\INFO301-ArchiLog\Chess-Ping
.\.venv\Scripts\Activate.ps1
python main.py
```
- Cliquez sur **"Créer une partie (Serveur)"**
- Notez l'IP affichée (probablement `127.0.0.1` ou votre IP locale)

3. **Terminal 2 - Client:**
```powershell
cd d:\mahasoa\ITU\S5\INFO301-ArchiLog\Chess-Ping
.\.venv\Scripts\Activate.ps1
python main.py
```
- Cliquez sur **"Rejoindre une partie (Client)"**
- Entrez IP: `127.0.0.1`
- Entrez Port: `5050`
- Cliquez **"Se connecter"**

4. **Configuration (Serveur uniquement):**
- Choisissez le nombre de lignes (2, 4, 6, ou 8)
- Configurez les pièces
- Choisissez qui commence
- Validez

5. **Jouez !**
- Serveur : `W`/`S` pour bouger le paddle gauche (**rouge**)
- Client : `↑`/`↓` pour bouger le paddle droit (**bleu**)
- `Espace` ou Clic pour lancer la balle

---

## 🚀 Méthode Automatique

Utilisez le script de test :

```powershell
cd d:\mahasoa\ITU\S5\INFO301-ArchiLog\Chess-Ping
.\test_multiplayer.ps1
```

Cela ouvrira automatiquement deux fenêtres. Suivez les instructions affichées.

---

## 🌐 Test sur Réseau Local (2 PCs)

### PC Serveur (Hôte)
```powershell
cd d:\mahasoa\ITU\S5\INFO301-ArchiLog\Chess-Ping
.\.venv\Scripts\Activate.ps1
python main.py
```
- Choisissez **"Créer une partie (Serveur)"**
- **Notez bien l'IP affichée** (ex: `192.168.1.100`)
- Donnez cette IP au joueur 2

### PC Client (Invité)
```powershell
cd d:\mahasoa\ITU\S5\INFO301-ArchiLog\Chess-Ping
.\.venv\Scripts\Activate.ps1
python main.py
```
- Choisissez **"Rejoindre une partie (Client)"**
- Entrez l'IP du serveur (donnée par le joueur 1)
- Entrez Port: `5050`
- Cliquez **"Se connecter"**

---

## 🎯 Contrôles

| Joueur | Paddle | Monter | Descendre | Lancer Balle |
|--------|--------|--------|-----------|--------------|
| Serveur (Hôte) | Gauche (Rouge) | `W` | `S` | `Espace` / Clic |
| Client (Invité) | Droit (Bleu) | `↑` | `↓` | `Espace` / Clic |

---

## ❓ Problèmes Fréquents

### ❌ "Erreur de connexion"
**Solution:** Le serveur n'est pas démarré. Lancez d'abord le serveur, puis le client.

### ❌ "Waiting for connection..." ne se termine pas
**Solutions:**
1. Vérifiez que vous utilisez la bonne IP
2. Vérifiez le pare-feu Windows :
```powershell
# En tant qu'Administrateur
New-NetFirewallRule -DisplayName "Chess-Ping" -Direction Inbound -Protocol TCP -LocalPort 5050 -Action Allow
```

### ❌ Le jeu se désynchronise
**Solution:** Redémarrez les deux instances. La latence réseau est peut-être trop élevée.

### ❌ Port 5050 déjà utilisé
**Solution:** Fermez toutes les instances de Chess-Ping et réessayez.

---

## 📖 Documentation Complète

Pour plus de détails, consultez :
- **`MULTIPLAYER_README.md`** - Documentation complète du mode réseau
- **`IMPLEMENTATION_SUMMARY.md`** - Détails techniques de l'implémentation
- **`ARCHITECTURE_DIAGRAM.txt`** - Diagramme de l'architecture

---

## 🎓 Concepts Clés

**Serveur (Authoritative):**
- Calcule la physique du jeu
- Détecte les collisions
- Envoie les mises à jour aux clients

**Client (Replicative):**
- Contrôle son paddle
- Reçoit et affiche l'état du jeu
- Fait confiance au serveur pour la physique

**Synchronisation:**
- Messages JSON échangés en temps réel
- ~60 mises à jour par seconde
- Communication bidirectionnelle non-bloquante

---

## 💡 Astuces

1. **Meilleure performance:** Utilisez un réseau câblé (Ethernet) plutôt que Wi-Fi
2. **Test rapide:** Utilisez toujours `127.0.0.1` pour tester en local
3. **IP locale:** Si l'IP affichée est `127.0.0.1` mais vous voulez jouer en réseau, utilisez `ipconfig` pour trouver votre vraie IP locale
4. **Latence:** Pour une expérience fluide, la latence réseau doit être < 50ms

---

## ✅ Checklist de Test

- [ ] Le menu principal affiche 3 boutons
- [ ] Mode serveur démarre et affiche l'IP
- [ ] Mode client peut saisir IP et port
- [ ] Client se connecte avec succès au serveur
- [ ] Configuration de partie fonctionne côté serveur
- [ ] Client reçoit la configuration automatiquement
- [ ] Les deux paddles bougent correctement
- [ ] La balle se synchronise entre serveur et client
- [ ] Les collisions fonctionnent
- [ ] Les scores se mettent à jour
- [ ] Les pièces perdent de la vie
- [ ] Le jeu se termine quand toutes les pièces d'un camp sont détruites

---

**Amusez-vous bien ! 🎮🏓♟️**
