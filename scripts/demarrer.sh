#!/usr/bin/env bash
# SOLIDA -- installation et démarrage en une commande (Linux / macOS / Git Bash / WSL).
# Usage : ./scripts/demarrer.sh
#
# Ce script ne demande rien d'autre que d'être lancé : il vérifie Docker, génère la
# configuration locale si elle manque, construit les images, démarre la pile, attend
# qu'elle réponde vraiment, puis indique l'URL à ouvrir. Sans argument, sans prérequis
# manuel au-delà de Docker Desktop installé et démarré.
set -uo pipefail

# ------------------------------------------------------------------ present­ation
RESET=$'\033[0m'; BOLD=$'\033[1m'; DIM=$'\033[2m'
ROUGE=$'\033[31m'; VERT=$'\033[32m'; JAUNE=$'\033[33m'
BLEU=$'\033[34m'; CYAN=$'\033[36m'; GRIS=$'\033[90m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$RACINE"

etape_num=0
horodatage_debut=$(date +%s)

banniere() {
  printf '%s\n' "${CYAN}${BOLD}"
  cat <<'EOF'
   _____ ______  __    ______  ___
  / __(_) __ \ \/ /   / _/ _ \/ _/
 _\ \/ / /_/ /\  /   /_ / // / _/
/___/_/\____/ /_/  /___/____/_/
EOF
  printf '%s\n' "${RESET}${DIM}  Scoring d'octroi de microcrédit -- coopératives financières${RESET}"
  printf '%s\n\n' "${DIM}  Installation et démarrage automatiques${RESET}"
}

etape() {
  etape_num=$((etape_num + 1))
  printf '\n%s%s▶ Étape %d — %s%s\n' "${BLEU}" "${BOLD}" "$etape_num" "$1" "${RESET}"
}

ok()   { printf '  %s✔ %s%s\n' "${VERT}" "$1" "${RESET}"; }
info() { printf '  %s• %s%s\n' "${GRIS}" "$1" "${RESET}"; }
avert(){ printf '  %s⚠ %s%s\n' "${JAUNE}" "$1" "${RESET}"; }

echouer() {
  printf '\n  %s✘ %s%s\n' "${ROUGE}${BOLD}" "$1" "${RESET}"
  if [ -n "${2:-}" ]; then
    printf '  %s%s%s\n' "${GRIS}" "$2" "${RESET}"
  fi
  printf '\n%sArrêt. Rien de plus n'"'"'a été modifié.%s\n' "${ROUGE}" "${RESET}"
  exit 1
}

# Exécute une commande docker en affichant sa sortie réelle (pas de faux spinner qui
# masquerait une erreur utile), et arrête tout net si elle échoue.
executer() {
  local description="$1"; shift
  printf '  %s→ %s%s\n' "${GRIS}" "$description" "${RESET}"
  if ! "$@"; then
    echouer "$description a échoué." "Commande : $*"
  fi
}

gen_secret() {
  local longueur="${1:-32}"
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 96 | tr -dc 'A-Za-z0-9' | head -c "$longueur"
  else
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c "$longueur"
  fi
}

# ------------------------------------------------------------------ etape 1 : Docker
verifier_docker() {
  etape "Vérification de Docker"

  if ! command -v docker >/dev/null 2>&1; then
    echouer "Docker n'est pas installé (ou pas dans le PATH)." \
      "Installer Docker Desktop : https://www.docker.com/products/docker-desktop/ puis relancer ce script."
  fi
  ok "Docker CLI détecté ($(docker --version 2>/dev/null))"

  if ! docker info >/dev/null 2>&1; then
    echouer "Docker est installé mais ne répond pas." \
      "Démarrer Docker Desktop (ou le service docker), attendre l'icône \"running\", puis relancer ce script."
  fi
  ok "Le moteur Docker répond"

  if ! docker compose version >/dev/null 2>&1; then
    echouer "Le plugin \"docker compose\" (v2) est introuvable." \
      "Mettre à jour Docker Desktop -- ce projet utilise la syntaxe \"docker compose\" (v2), pas l'ancien \"docker-compose\"."
  fi
  ok "docker compose v2 disponible ($(docker compose version --short 2>/dev/null))"
}

# ------------------------------------------------------------------ etape 2 : configuration
configurer_env() {
  etape "Configuration locale (.env)"
  PREMIERE_INSTALLATION=0

  if [ -f "$RACINE/.env" ]; then
    ok "Configuration racine existante conservée (.env déjà présent, pas touché)"
  else
    PREMIERE_INSTALLATION=1
    info "Aucun .env : génération de mots de passe et secrets locaux aléatoires"

    local mdp_coresim_admin mdp_solida_app mdp_solida_lecteur mdp_solida_lecture
    local cle_acces_sw cle_secrete_sw secret_auth
    mdp_coresim_admin=$(gen_secret 32)
    mdp_solida_app=$(gen_secret 32)
    mdp_solida_lecteur=$(gen_secret 32)
    mdp_solida_lecture=$(gen_secret 32)
    cle_acces_sw=$(gen_secret 24)
    cle_secrete_sw=$(gen_secret 32)
    secret_auth=$(gen_secret 48)

    cat > "$RACINE/.env" <<EOF
# Généré automatiquement par scripts/demarrer.sh le $(date '+%Y-%m-%d %H:%M') -- usage local
# uniquement. Jamais commité (voir .gitignore). Pour régénérer : supprimer ce fichier
# puis relancer le script.

CORESIM_ADMIN_USER=coresim_admin
CORESIM_ADMIN_PASSWORD=${mdp_coresim_admin}

SOLIDA_APP_USER=solida_app
SOLIDA_APP_PASSWORD=${mdp_solida_app}

SOLIDA_LECTEUR_PASSWORD=${mdp_solida_lecteur}
SOLIDA_LECTURE_PASSWORD=${mdp_solida_lecture}

CORESIM_DATABASE_URL=postgresql+psycopg://solida_lecteur:${mdp_solida_lecteur}@postgres-coresim:5432/coresim
SOLIDA_DATABASE_URL=postgresql+psycopg://solida_app:${mdp_solida_app}@postgres-solida:5432/solida
SOLIDA_DATABASE_URL_ASYNC=postgresql+psycopg://solida_app:${mdp_solida_app}@postgres-solida:5432/solida

SEAWEEDFS_ACCESS_KEY=${cle_acces_sw}
SEAWEEDFS_SECRET_KEY=${cle_secrete_sw}

SECRET_AUTH=${secret_auth}
ENVIRONNEMENT=developpement
EOF
    ok ".env généré (secrets propres à cette machine)"
  fi

  if [ -f "$RACINE/frontend/.env" ]; then
    ok "Configuration frontend existante conservée (frontend/.env déjà présent)"
  else
    cp "$RACINE/frontend/.env.example" "$RACINE/frontend/.env"
    ok "frontend/.env généré depuis frontend/.env.example"
  fi
}

# ------------------------------------------------------------------ etape 3 : images
construire_images() {
  etape "Construction des images Docker (peut prendre plusieurs minutes la première fois)"
  executer "Construction" docker compose build
  ok "Images construites"
}

# ------------------------------------------------------------------ etape 4 : demarrage
demarrer_services() {
  etape "Démarrage des services"
  executer "Démarrage en arrière-plan" docker compose up -d
  ok "Conteneurs démarrés"
}

# ------------------------------------------------------------------ etape 5 : attente
attendre_disponibilite() {
  etape "Attente de la disponibilité réelle de l'application"
  local max_secondes=180 attente=0
  local pret_api=0 pret_front=0

  while [ "$attente" -lt "$max_secondes" ]; do
    if [ "$pret_api" -eq 0 ] && curl -fsS -o /dev/null "http://localhost/api/v1/health" 2>/dev/null; then
      pret_api=1; ok "API accessible (http://localhost/api/v1/health)"
    fi
    if [ "$pret_front" -eq 0 ] && curl -fsS -o /dev/null "http://localhost/" 2>/dev/null; then
      pret_front=1; ok "Interface accessible (http://localhost/)"
    fi
    if [ "$pret_api" -eq 1 ] && [ "$pret_front" -eq 1 ]; then
      return 0
    fi
    printf '  %s… en attente (%ds/%ds)%s\r' "${GRIS}" "$attente" "$max_secondes" "${RESET}"
    sleep 3
    attente=$((attente + 3))
  done

  printf '\n'
  echouer "L'application ne répond toujours pas après ${max_secondes}s." \
    "Voir les journaux : docker compose logs --tail=100 nginx api front   |   Le port 80 est-il déjà utilisé par un autre programme ?"
}

# ------------------------------------------------------------------ etape 6 : donnees (premiere fois seulement)
initialiser_donnees() {
  if [ "$PREMIERE_INSTALLATION" -ne 1 ]; then
    etape "Données"
    info "Configuration déjà existante : migrations rejouées par sécurité, données et comptes non touchés."
    executer "Migrations de schéma" docker compose run --rm api alembic upgrade head
    ok "Schéma à jour"
    return 0
  fi

  etape "Initialisation des données (première installation)"
  executer "Migrations de schéma (base solida)" docker compose run --rm api alembic upgrade head
  executer "Génération des données CORE-SIM" docker compose run --rm coresim-seed
  executer "Comptes de démonstration" docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes demo
  ok "Données et comptes de démonstration prêts"
}

# ------------------------------------------------------------------ conclusion
conclure() {
  local duree=$(( $(date +%s) - horodatage_debut ))
  printf '\n\n%s' "${VERT}${BOLD}"
  cat <<'EOF'
  ╔══════════════════════════════════════════════════════════════╗
  ║               SOLIDA EST PRÊT ET ACCESSIBLE                  ║
  ╚══════════════════════════════════════════════════════════════╝
EOF
  printf '%s\n' "${RESET}"
  printf '  %sOuvrir :%s  %s%shttp://localhost%s\n\n' "${BOLD}" "${RESET}" "${BOLD}" "${CYAN}" "${RESET}"

  if [ "$PREMIERE_INSTALLATION" -eq 1 ]; then
    printf '  %sComptes de démonstration (mot de passe : solida-demo) :%s\n' "${BOLD}" "${RESET}"
    printf '    agent.be              agent\n'
    printf '    agent.agoe            agent\n'
    printf '    superviseur.reseau    superviseur\n'
    printf '    auditeur.interne      auditeur\n'
    printf '    administrateur.systeme administrateur\n\n'
  fi

  printf '  %sPrêt en %ds. Pour arrêter : %sdocker compose down%s\n\n' "${GRIS}" "$duree" "${BOLD}" "${RESET}"
}

# ------------------------------------------------------------------ main
banniere
verifier_docker
configurer_env
construire_images
demarrer_services
attendre_disponibilite
initialiser_donnees
conclure
