# Script de test du mode multijoueur Chess-Ping
# Lance automatiquement un serveur et un client dans deux fenêtres séparées

Write-Host "Lancement du mode multijoueur Chess-Ping..." -ForegroundColor Cyan
Write-Host ""

# Obtenir le répertoire du script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Vérifier que l'environnement virtuel existe
$VenvPath = Join-Path $ScriptDir ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $VenvPath)) {
    Write-Host "ERREUR: L'environnement virtuel n'existe pas!" -ForegroundColor Red
    Write-Host "Créez-le avec: py -3.14 -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "1. Lancement du SERVEUR dans une nouvelle fenêtre..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ScriptDir'; .\.venv\Scripts\Activate.ps1; Write-Host 'SERVEUR: Sélectionnez Créer une partie (Serveur)' -ForegroundColor Yellow; python main.py"
)

Write-Host "   Attendez 2 secondes..." -ForegroundColor Gray
Start-Sleep -Seconds 2

Write-Host "2. Lancement du CLIENT dans une nouvelle fenêtre..." -ForegroundColor Green  
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ScriptDir'; .\.venv\Scripts\Activate.ps1; Write-Host 'CLIENT: Sélectionnez Rejoindre une partie (Client), IP: 127.0.0.1, Port: 5050' -ForegroundColor Yellow; python main.py"
)

Write-Host ""
Write-Host "Les deux fenêtres sont lancées!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Instructions:" -ForegroundColor White
Write-Host "  1. Dans la fenêtre SERVEUR: Cliquez sur 'Créer une partie (Serveur)'" -ForegroundColor White
Write-Host "  2. Notez l'IP affichée (devrait être 127.0.0.1 ou votre IP locale)" -ForegroundColor White
Write-Host "  3. Dans la fenêtre CLIENT: Cliquez sur 'Rejoindre une partie (Client)'" -ForegroundColor White
Write-Host "  4. Entrez IP: 127.0.0.1 et Port: 5050" -ForegroundColor White
Write-Host "  5. Une fois connectés, configurez la partie côté serveur" -ForegroundColor White
Write-Host "  6. Lancez la partie et jouez!" -ForegroundColor White
Write-Host ""
Write-Host "Contrôles:" -ForegroundColor White
Write-Host "  Serveur (paddle gauche): W/S" -ForegroundColor White
Write-Host "  Client (paddle droit): Flèches Haut/Bas" -ForegroundColor White
Write-Host ""
