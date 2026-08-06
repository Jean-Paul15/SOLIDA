#requires -version 5.1
<#
.SYNOPSIS
    SOLIDA -- installation et démarrage en une commande (Windows).
.DESCRIPTION
    Ne demande rien d'autre que d'être lancé : vérifie Docker, génère la configuration
    locale si elle manque, construit les images, démarre la pile, attend qu'elle réponde
    vraiment, puis indique l'URL à ouvrir. Prérequis : Docker Desktop installé et démarré.
.EXAMPLE
    .\scripts\demarrer.ps1
#>

$ErrorActionPreference = "Stop"
$RACINE = Split-Path -Parent $PSScriptRoot
Set-Location $RACINE

$script:EtapeNum = 0
$script:HorodatageDebut = Get-Date
$script:PremiereInstallation = $false

function Show-Banniere {
    Write-Host ""
    Write-Host "   _____ ______  __    ______  ___" -ForegroundColor Cyan
    Write-Host "  / __(_) __ \ \/ /   / _/ _ \/ _/" -ForegroundColor Cyan
    Write-Host " _\ \/ / /_/ /\  /   /_ / // / _/" -ForegroundColor Cyan
    Write-Host "/___/_/\____/ /_/  /___/____/_/" -ForegroundColor Cyan
    Write-Host "  Scoring d'octroi de microcrédit -- coopératives financières" -ForegroundColor DarkGray
    Write-Host "  Installation et démarrage automatiques" -ForegroundColor DarkGray
    Write-Host ""
}

function Show-Etape([string]$Titre) {
    $script:EtapeNum++
    Write-Host ""
    Write-Host "▶ Étape $($script:EtapeNum) — $Titre" -ForegroundColor Blue -BackgroundColor Black
}

function Show-Ok([string]$Message) { Write-Host "  ✔ $Message" -ForegroundColor Green }
function Show-Info([string]$Message) { Write-Host "  • $Message" -ForegroundColor DarkGray }
function Show-Avertissement([string]$Message) { Write-Host "  ⚠ $Message" -ForegroundColor Yellow }

function Stop-AvecErreur([string]$Message, [string]$Detail = "") {
    Write-Host ""
    Write-Host "  ✘ $Message" -ForegroundColor Red
    if ($Detail) { Write-Host "  $Detail" -ForegroundColor DarkGray }
    Write-Host ""
    Write-Host "Arrêt. Rien de plus n'a été modifié." -ForegroundColor Red
    exit 1
}

# Exécute une commande externe en affichant sa sortie réelle (pas de faux spinner qui
# masquerait une erreur utile), et arrête tout net si elle échoue.
function Invoke-Etape([string]$Description, [scriptblock]$Commande) {
    Write-Host "  → $Description" -ForegroundColor DarkGray
    & $Commande
    if ($LASTEXITCODE -ne 0) {
        Stop-AvecErreur "$Description a échoué." "Code de sortie : $LASTEXITCODE"
    }
}

function New-Secret([int]$Longueur = 32) {
    $octets = [System.Security.Cryptography.RandomNumberGenerator]::GetBytes($Longueur * 2)
    $brut = [Convert]::ToBase64String($octets)
    $filtre = ($brut -replace '[^A-Za-z0-9]', '')
    return $filtre.Substring(0, [Math]::Min($Longueur, $filtre.Length))
}

# ------------------------------------------------------------------ etape 1 : Docker
function Test-Docker {
    Show-Etape "Vérification de Docker"

    $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCmd) {
        Stop-AvecErreur "Docker n'est pas installé (ou pas dans le PATH)." `
            "Installer Docker Desktop : https://www.docker.com/products/docker-desktop/ puis relancer ce script."
    }
    $version = (docker --version) 2>$null
    Show-Ok "Docker CLI détecté ($version)"

    docker info *>$null
    if ($LASTEXITCODE -ne 0) {
        Stop-AvecErreur "Docker est installé mais ne répond pas." `
            "Démarrer Docker Desktop, attendre l'icône ""running"" (baleine fixe, pas animée), puis relancer ce script."
    }
    Show-Ok "Le moteur Docker répond"

    docker compose version *>$null
    if ($LASTEXITCODE -ne 0) {
        Stop-AvecErreur "Le plugin ""docker compose"" (v2) est introuvable." `
            "Mettre à jour Docker Desktop -- ce projet utilise la syntaxe ""docker compose"" (v2), pas l'ancien ""docker-compose""."
    }
    $composeVersion = (docker compose version --short) 2>$null
    Show-Ok "docker compose v2 disponible ($composeVersion)"
}

# ------------------------------------------------------------------ etape 2 : configuration
function Set-Configuration {
    Show-Etape "Configuration locale (.env)"

    $envRacine = Join-Path $RACINE ".env"
    if (Test-Path $envRacine) {
        Show-Ok "Configuration racine existante conservée (.env déjà présent, pas touché)"
    }
    else {
        $script:PremiereInstallation = $true
        Show-Info "Aucun .env : génération de mots de passe et secrets locaux aléatoires"

        $mdpCoresimAdmin  = New-Secret 32
        $mdpSolidaApp     = New-Secret 32
        $mdpSolidaLecteur = New-Secret 32
        $mdpSolidaLecture = New-Secret 32
        $cleAccesSw       = New-Secret 24
        $cleSecreteSw     = New-Secret 32
        $secretAuth       = New-Secret 48

        $horodatage = Get-Date -Format "yyyy-MM-dd HH:mm"
        $contenu = @"
# Généré automatiquement par scripts/demarrer.ps1 le $horodatage -- usage local
# uniquement. Jamais commité (voir .gitignore). Pour régénérer : supprimer ce fichier
# puis relancer le script.

CORESIM_ADMIN_USER=coresim_admin
CORESIM_ADMIN_PASSWORD=$mdpCoresimAdmin

SOLIDA_APP_USER=solida_app
SOLIDA_APP_PASSWORD=$mdpSolidaApp

SOLIDA_LECTEUR_PASSWORD=$mdpSolidaLecteur
SOLIDA_LECTURE_PASSWORD=$mdpSolidaLecture

CORESIM_DATABASE_URL=postgresql+psycopg://solida_lecteur:$mdpSolidaLecteur@postgres-coresim:5432/coresim
SOLIDA_DATABASE_URL=postgresql+psycopg://solida_app:$mdpSolidaApp@postgres-solida:5432/solida
SOLIDA_DATABASE_URL_ASYNC=postgresql+psycopg://solida_app:$mdpSolidaApp@postgres-solida:5432/solida

SEAWEEDFS_ACCESS_KEY=$cleAccesSw
SEAWEEDFS_SECRET_KEY=$cleSecreteSw

SECRET_AUTH=$secretAuth
ENVIRONNEMENT=developpement
"@
        [System.IO.File]::WriteAllText($envRacine, $contenu, [System.Text.Encoding]::UTF8)
        Show-Ok ".env généré (secrets propres à cette machine)"
    }

    $envFront = Join-Path $RACINE "frontend\.env"
    if (Test-Path $envFront) {
        Show-Ok "Configuration frontend existante conservée (frontend\.env déjà présent)"
    }
    else {
        Copy-Item (Join-Path $RACINE "frontend\.env.example") $envFront
        Show-Ok "frontend\.env généré depuis frontend\.env.example"
    }
}

# ------------------------------------------------------------------ etape 3 : images
function Build-Images {
    Show-Etape "Construction des images Docker (peut prendre plusieurs minutes la première fois)"
    Invoke-Etape "Construction" { docker compose build }
    Show-Ok "Images construites"
}

# ------------------------------------------------------------------ etape 4 : demarrage
function Start-Services {
    Show-Etape "Démarrage des services"
    Invoke-Etape "Démarrage en arrière-plan" { docker compose up -d }
    Show-Ok "Conteneurs démarrés"
}

# ------------------------------------------------------------------ etape 5 : attente
function Wait-Disponibilite {
    Show-Etape "Attente de la disponibilité réelle de l'application"
    $maxSecondes = 180
    $attente = 0
    $pretApi = $false
    $pretFront = $false

    while ($attente -lt $maxSecondes) {
        if (-not $pretApi) {
            try {
                $r = Invoke-WebRequest -Uri "http://localhost/api/v1/sante" -UseBasicParsing -TimeoutSec 5
                if ($r.StatusCode -eq 200) { $pretApi = $true; Show-Ok "API accessible (http://localhost/api/v1/sante)" }
            } catch {}
        }
        if (-not $pretFront) {
            try {
                $r = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing -TimeoutSec 5
                if ($r.StatusCode -eq 200) { $pretFront = $true; Show-Ok "Interface accessible (http://localhost/)" }
            } catch {}
        }
        if ($pretApi -and $pretFront) { return }

        Write-Host "  … en attente ($attente s / $maxSecondes s)" -ForegroundColor DarkGray -NoNewline
        Write-Host "`r" -NoNewline
        Start-Sleep -Seconds 3
        $attente += 3
    }

    Stop-AvecErreur "L'application ne répond toujours pas après $maxSecondes s." `
        "Voir les journaux : docker compose logs --tail=100 nginx api front   |   Le port 80 est-il déjà utilisé par un autre programme (IIS, Skype, un autre serveur) ?"
}

# ------------------------------------------------------------------ etape 6 : donnees (premiere fois seulement)
function Initialize-Donnees {
    if (-not $script:PremiereInstallation) {
        Show-Etape "Données"
        Show-Info "Configuration déjà existante : migrations rejouées par sécurité, données et comptes non touchés."
        Invoke-Etape "Migrations de schéma" { docker compose run --rm api alembic upgrade head }
        return
    }

    Show-Etape "Initialisation des données (première installation)"
    Invoke-Etape "Migrations de schéma (base solida)" { docker compose run --rm api alembic upgrade head }
    Invoke-Etape "Génération des données CORE-SIM" { docker compose run --rm coresim-seed }
    Invoke-Etape "Comptes de démonstration" { docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes demo }
    Show-Ok "Données et comptes de démonstration prêts"
}

# ------------------------------------------------------------------ conclusion
function Show-Conclusion {
    $duree = [int]((Get-Date) - $script:HorodatageDebut).TotalSeconds
    Write-Host ""
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║               SOLIDA EST PRÊT ET ACCESSIBLE                  ║" -ForegroundColor Green
    Write-Host "  ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Ouvrir :  " -NoNewline -ForegroundColor White
    Write-Host "http://localhost" -ForegroundColor Cyan
    Write-Host ""

    if ($script:PremiereInstallation) {
        Write-Host "  Comptes de démonstration (mot de passe : solida-demo) :" -ForegroundColor White
        Write-Host "    agent.be                agent"
        Write-Host "    agent.agoe              agent"
        Write-Host "    superviseur.reseau      superviseur"
        Write-Host "    auditeur.interne        auditeur"
        Write-Host "    administrateur.systeme  administrateur"
        Write-Host ""
    }

    Write-Host "  Prêt en $duree s. Pour arrêter : docker compose down" -ForegroundColor DarkGray
    Write-Host ""
}

# ------------------------------------------------------------------ main
try {
    Show-Banniere
    Test-Docker
    Set-Configuration
    Build-Images
    Start-Services
    Wait-Disponibilite
    Initialize-Donnees
    Show-Conclusion
}
catch {
    Stop-AvecErreur "Erreur inattendue : $($_.Exception.Message)" ($_.ScriptStackTrace)
}
