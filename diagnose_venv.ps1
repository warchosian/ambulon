# Diagnostique de l'environnement virtuel Python
# Résout l'erreur "No pyvenv.cfg file"

$projectDir = "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
$venvPath = Join-Path $projectDir ".venv"
$pyvenvCfgPath = Join-Path $venvPath "pyvenv.cfg"

Write-Host "=== Diagnostic environnement virtuel ===" -ForegroundColor Cyan
Write-Host "Répertoire projet : $projectDir"
Write-Host ""

# 1. Vérification du dossier .venv
Write-Host "[1] Dossier .venv : " -NoNewline
if (Test-Path $venvPath -PathType Container) {
    Write-Host "EXISTS" -ForegroundColor Green
} else {
    Write-Host "MANQUANT" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solution : Créer l'environnement avec : python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# 2. Vérification de pyvenv.cfg
Write-Host "[2] Fichier pyvenv.cfg : " -NoNewline
if (Test-Path $pyvenvCfgPath -PathType Leaf) {
    Write-Host "EXISTS" -ForegroundColor Green
} else {
    Write-Host "MANQUANT" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solution : Le dossier .venv est corrompu. Supprimez-le et recréez-le :" -ForegroundColor Yellow
    Write-Host "  rmdir /s /q .venv" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# 3. Contenu de pyvenv.cfg
Write-Host "[3] Contenu de pyvenv.cfg :" -ForegroundColor Cyan
Get-Content $pyvenvCfgPath | ForEach-Object { Write-Host "    $_" }
Write-Host ""

# 4. Vérification de Python dans PATH
Write-Host "[4] Python dans PATH : " -NoNewline
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    Write-Host "TROUVÉ" -ForegroundColor Green
    Write-Host "    Chemin : $($pythonCmd.Source)"
} else {
    Write-Host "NON TROUVÉ" -ForegroundColor Red
}

# 5. Version de Python
Write-Host "[5] Version Python : " -NoNewline
try {
    $version = python --version 2>&1
    Write-Host $version -ForegroundColor Green
} catch {
    Write-Host "ERREUR" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Diagnostic terminé ===" -ForegroundColor Cyan
