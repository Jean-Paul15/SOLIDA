"""Interface CLI d'administration des comptes SOLIDA.

La création, le blocage et le déblocage ne sont jamais exposés par HTTP.
"""

import argparse

from solida.adapters.persistence.orm_models import ROLES_VALIDES
from solida.infrastructure.account_provisioning import (
    create_account,
    list_locked_accounts,
    lock_account,
    provision_demo,
    unlock_account,
)

__all__ = [
    "create_account",
    "list_locked_accounts",
    "lock_account",
    "provision_demo",
    "unlock_account",
]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="Provisionne les comptes de démonstration.")

    create = subparsers.add_parser("creer", help="Crée ou met à jour un compte.")
    create.add_argument("--identifiant", required=True)
    create.add_argument("--nom", required=True, dest="nom_complet")
    create.add_argument("--role", required=True, choices=ROLES_VALIDES)
    create.add_argument("--agence", default=None, dest="agence_id")
    create.add_argument("--email", default=None)

    lock = subparsers.add_parser("bloquer", help="Désactive un compte existant.")
    lock.add_argument("--identifiant", required=True)

    unlock = subparsers.add_parser("debloquer", help="Réactive un compte désactivé.")
    unlock.add_argument("--identifiant", required=True)
    subparsers.add_parser("lister-bloques", help="Liste les comptes désactivés.")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    if args.command == "demo":
        provision_demo()
        print("Comptes de démonstration provisionnés (mot de passe partagé).")
    elif args.command == "creer":
        password = create_account(
            identifiant=args.identifiant,
            nom_complet=args.nom_complet,
            role=args.role,
            agence_id=args.agence_id,
            email=args.email,
        )
        print(f"Compte '{args.identifiant}' créé. Mot de passe initial : {password}")
        print("À changer obligatoirement à la première connexion.")
    elif args.command == "bloquer":
        lock_account(args.identifiant)
        print(f"Compte '{args.identifiant}' désactivé et ses sessions révoquées.")
    elif args.command == "debloquer":
        unlock_account(args.identifiant)
        print(f"Compte '{args.identifiant}' réactivé.")
    else:
        accounts = list_locked_accounts()
        if not accounts:
            print("Aucun compte désactivé.")
        for account in accounts:
            print(
                f"{account.identifiant} — {account.nom_complet} ({account.role}, "
                f"{account.agence_id or 'sans agence'}) — désactivé le {account.desactive_le}"
            )


if __name__ == "__main__":
    main()
