"""Gestion des comptes utilisateurs SOLIDA — création et blocage.

Aucun endpoint HTTP ne permet de créer ou débloquer un compte : c'est un choix de
sécurité délibéré (surface d'attaque nulle sur la gestion des comptes). Ce script,
exécuté manuellement dans le conteneur, est l'unique moyen d'y toucher — pour la
démonstration comme pour une exploitation réelle, sans distinction. Seule différence :
les comptes de démonstration (`demo`) n'exigent pas de changer leur mot de passe
partagé à la première connexion, contrairement à tout compte créé via `creer`.

Usage :
  docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes demo
  docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes creer \
      --identifiant agent.lome --nom "Agent Lomé" --role agent --agence CAI-02
  docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes bloquer \
      --identifiant agent.lome
  docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes debloquer \
      --identifiant agent.lome
  docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes \
      lister-bloques
"""

import argparse
import secrets
import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from fastapi_users.password import PasswordHelper

from solida.adapters.persistence.modeles_sqlalchemy import ROLES_VALIDES
from solida.infrastructure.database import solida_engine

MOT_DE_PASSE_DEMO = "solida-demo"

COMPTES_DEMO: list[dict[str, str | None]] = [
    {
        "identifiant": "agent.be",
        "email": "agent.be@solida.local",
        "nom_complet": "Agent Bè",
        "role": "agent",
        "agence_id": "CAI-00",
    },
    {
        "identifiant": "agent.agoe",
        "email": "agent.agoe@solida.local",
        "nom_complet": "Agent Agoè",
        "role": "agent",
        "agence_id": "CAI-01",
    },
    {
        "identifiant": "superviseur.reseau",
        "email": "superviseur.reseau@solida.local",
        "nom_complet": "Superviseur Réseau",
        "role": "superviseur",
        "agence_id": None,
    },
    {
        "identifiant": "auditeur.interne",
        "email": "auditeur.interne@solida.local",
        "nom_complet": "Auditeur Interne",
        "role": "auditeur",
        "agence_id": None,
    },
    {
        "identifiant": "administrateur.systeme",
        "email": "administrateur.systeme@solida.local",
        "nom_complet": "Administrateur Système",
        "role": "administrateur",
        "agence_id": None,
    },
]


def _generate_password() -> str:
    return secrets.token_urlsafe(12)


def creer_compte(
    identifiant: str,
    nom_complet: str,
    role: str,
    agence_id: str | None,
    email: str | None = None,
    mot_de_passe: str | None = None,
    doit_changer_mot_de_passe: bool = True,
) -> str:
    """Crée le compte, ou met à jour nom/rôle/agence s'il existe déjà (idempotent par
    `identifiant`). Le mot de passe n'est jamais réémis sur un compte déjà existant —
    seule une création initiale ou un déblocage explicite en fixe un nouveau. Renvoie
    le mot de passe en clair (généré si non fourni) pour communication hors-bande.
    `doit_changer_mot_de_passe=False` réservé aux comptes de démonstration (voir
    `provisionner_demo`) : pour un vrai compte, le changement forcé reste la règle."""
    if role not in ROLES_VALIDES:
        raise SystemExit(f"Rôle invalide : {role!r}. Attendu : {ROLES_VALIDES}.")

    mot_de_passe_final = mot_de_passe or _generate_password()
    hachage = PasswordHelper().hash(mot_de_passe_final)
    instruction = sa.text("""
        INSERT INTO utilisateur
            (id, identifiant, nom_complet, role, agence_id, email,
             hashed_password, is_active, is_superuser, is_verified,
             doit_changer_mot_de_passe)
        VALUES
            (:id, :identifiant, :nom_complet, :role, :agence_id, :email,
             :hashed_password, true, false, true, :doit_changer_mot_de_passe)
        ON CONFLICT (identifiant) DO UPDATE SET
            nom_complet = excluded.nom_complet,
            role = excluded.role,
            agence_id = excluded.agence_id,
            doit_changer_mot_de_passe = excluded.doit_changer_mot_de_passe
    """)
    with solida_engine().begin() as connexion:
        connexion.execute(
            instruction,
            {
                "id": uuid.uuid4(),
                "identifiant": identifiant,
                "nom_complet": nom_complet,
                "role": role,
                "agence_id": agence_id,
                "email": email or f"{identifiant}@solida.local",
                "hashed_password": hachage,
                "doit_changer_mot_de_passe": doit_changer_mot_de_passe,
            },
        )
    return mot_de_passe_final


def provisionner_demo() -> None:
    # Comptes de test, jamais de vrais comptes : le changement de mot de passe forcé
    # ne servirait qu'à ralentir la démonstration, contrairement à un compte réel.
    for compte in COMPTES_DEMO:
        creer_compte(
            identifiant=compte["identifiant"] or "",
            nom_complet=compte["nom_complet"] or "",
            role=compte["role"] or "",
            agence_id=compte["agence_id"],
            email=compte["email"],
            mot_de_passe=MOT_DE_PASSE_DEMO,
            doit_changer_mot_de_passe=False,
        )
    print(f"{len(COMPTES_DEMO)} comptes de démonstration provisionnés (mot de passe partagé).")


def bloquer_compte(identifiant: str) -> None:
    with solida_engine().begin() as connexion:
        ligne = connexion.execute(
            sa.text("""
                UPDATE utilisateur SET is_active = false, desactive_le = :maintenant
                WHERE identifiant = :identifiant
                RETURNING id
            """),
            {"maintenant": datetime.now(UTC), "identifiant": identifiant},
        ).first()
        if ligne is None:
            raise SystemExit(f"Aucun compte avec l'identifiant '{identifiant}'.")
        # Un compte bloqué ne doit conserver aucune session déjà ouverte.
        connexion.execute(sa.text("DELETE FROM access_token WHERE user_id = :id"), {"id": ligne.id})
    print(f"Compte '{identifiant}' désactivé et ses sessions révoquées.")


def lister_comptes_bloques() -> list[dict[str, object]]:
    """Lecture seule : comptes désactivés (`is_active = false`), les plus récents d'abord.
    Un administrateur y décide ensuite, au cas par cas, d'un `debloquer` — cette fonction ne
    débloque jamais rien elle-même."""
    with solida_engine().connect() as connexion:
        lignes = connexion.execute(
            sa.text("""
                SELECT identifiant, nom_complet, role, agence_id, desactive_le
                FROM utilisateur
                WHERE is_active = false
                ORDER BY desactive_le DESC NULLS LAST
            """)
        )
        return [dict(ligne._mapping) for ligne in lignes]


def debloquer_compte(identifiant: str) -> None:
    with solida_engine().begin() as connexion:
        ligne = connexion.execute(
            sa.text("""
                UPDATE utilisateur SET is_active = true, desactive_le = NULL
                WHERE identifiant = :identifiant
                RETURNING id
            """),
            {"identifiant": identifiant},
        ).first()
        if ligne is None:
            raise SystemExit(f"Aucun compte avec l'identifiant '{identifiant}'.")
    print(f"Compte '{identifiant}' réactivé.")


def _build_parser() -> argparse.ArgumentParser:
    analyseur = argparse.ArgumentParser(description=__doc__)
    sous_commandes = analyseur.add_subparsers(dest="commande", required=True)

    sous_commandes.add_parser("demo", help="Provisionne les comptes de démonstration.")

    creer = sous_commandes.add_parser("creer", help="Crée ou met à jour un compte.")
    creer.add_argument("--identifiant", required=True)
    creer.add_argument("--nom", required=True, dest="nom_complet")
    creer.add_argument("--role", required=True, choices=ROLES_VALIDES)
    creer.add_argument("--agence", default=None, dest="agence_id")
    creer.add_argument("--email", default=None)

    bloquer = sous_commandes.add_parser("bloquer", help="Désactive un compte existant.")
    bloquer.add_argument("--identifiant", required=True)

    debloquer = sous_commandes.add_parser("debloquer", help="Réactive un compte désactivé.")
    debloquer.add_argument("--identifiant", required=True)

    sous_commandes.add_parser(
        "lister-bloques", help="Liste les comptes désactivés (lecture seule)."
    )

    return analyseur


def main() -> None:
    arguments = _build_parser().parse_args()
    if arguments.commande == "demo":
        provisionner_demo()
    elif arguments.commande == "creer":
        mot_de_passe = creer_compte(
            identifiant=arguments.identifiant,
            nom_complet=arguments.nom_complet,
            role=arguments.role,
            agence_id=arguments.agence_id,
            email=arguments.email,
        )
        print(f"Compte '{arguments.identifiant}' créé. Mot de passe initial : {mot_de_passe}")
        print("À changer obligatoirement à la première connexion.")
    elif arguments.commande == "bloquer":
        bloquer_compte(arguments.identifiant)
    elif arguments.commande == "debloquer":
        debloquer_compte(arguments.identifiant)
    elif arguments.commande == "lister-bloques":
        comptes = lister_comptes_bloques()
        if not comptes:
            print("Aucun compte désactivé.")
        for compte in comptes:
            print(
                f"{compte['identifiant']} — {compte['nom_complet']} ({compte['role']}, "
                f"{compte['agence_id'] or 'sans agence'}) — désactivé le {compte['desactive_le']}"
            )


if __name__ == "__main__":
    main()
