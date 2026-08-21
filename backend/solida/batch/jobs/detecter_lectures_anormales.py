"""Alerte sur un volume de lecture hors norme (recherche/dossier) par acteur.

Ne bloque jamais un compte : écrit une entrée `alerte_volume_lecture` dans `journal_audit`
pour qu'un superviseur/administrateur la revoie et décide, au cas par cas, d'utiliser le
blocage déjà existant (`cli_provisionner_comptes bloquer`) si c'est réellement anormal.
Volontairement pas d'automatisation du blocage lui-même : un seuil fixe qui bloquerait tout
seul serait lui-même un vecteur de déni de service (faire bloquer un agent légitime exprès),
et une simple journée chargée peut dépasser un seuil sans qu'il y ait le moindre problème.
Voir `docs/backend/07-monitoring-securite.md` pour le détail de cet arbitrage.

SEUIL : plus de 100 lectures (`recherche_societaires` + `consultation_dossier` cumulées) par
acteur sur une fenêtre glissante d'1 heure. Repris tel quel de la recommandation du rapport de
pentest round 3, pas une valeur inventée pour l'occasion — marqué comme ajustable dans
`03-MODELE/10-politique-credit-decisions-en-attente.md` : la vraie valeur dépend du volume
réel observé une fois l'application utilisée en production.

Ce job ne détecte que les pics au-dessus du seuil sur la fenêtre considérée — un vol "lent",
étalé et systématiquement sous le seuil, ne déclenche rien (limite connue, pas cachée).

Aucun ordonnanceur n'existe dans la pile SOLIDA (même limite que `purger_journal_audit.py`) :
ce script s'exécute manuellement ou via une tâche planifiée externe, par exemple :

  */15 * * * * docker compose run --rm api python -m solida.batch.jobs.detecter_lectures_anormales

Usage :
  docker compose run --rm api python -m solida.batch.jobs.detecter_lectures_anormales
  docker compose run --rm api python -m solida.batch.jobs.detecter_lectures_anormales \
      --essai-a-blanc
"""

import argparse
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

from solida.adapters.persistence.audit_log_sql import SqlAuditLog
from solida.infrastructure.database import solida_engine

logger = logging.getLogger(__name__)

FENETRE = timedelta(hours=1)
SEUIL_LECTURES = 100

TYPES_LECTURE = ("recherche_societaires", "consultation_dossier")


@dataclass(frozen=True)
class AlertedActor:
    acteur_id: str
    nombre_lectures: int


def detect(depuis: datetime | None = None) -> list[AlertedActor]:
    """Renvoie les acteurs ayant dépassé `SEUIL_LECTURES` lectures depuis `depuis`
    (par défaut : début de `FENETRE` avant maintenant), sans rien écrire."""
    seuil_temporel = depuis or (datetime.now(UTC) - FENETRE)
    instruction = sa.text("""
        SELECT acteur_id, count(*) AS nb
        FROM journal_audit
        WHERE type = ANY(:types) AND horodatage >= :depuis
        GROUP BY acteur_id
        HAVING count(*) > :seuil
        ORDER BY nb DESC
    """)
    with solida_engine().connect() as connexion:
        lignes = connexion.execute(
            instruction,
            {"types": list(TYPES_LECTURE), "depuis": seuil_temporel, "seuil": SEUIL_LECTURES},
        )
        return [
            AlertedActor(acteur_id=ligne.acteur_id, nombre_lectures=ligne.nb) for ligne in lignes
        ]


def alert(essai_a_blanc: bool = False) -> list[AlertedActor]:
    """Détecte puis, sauf essai à blanc, journalise une entrée `alerte_volume_lecture` par
    acteur en dépassement. Ne touche jamais à `utilisateur` : aucun blocage automatique."""
    depasses = detect()
    if essai_a_blanc or not depasses:
        return depasses

    audit = SqlAuditLog(solida_engine())
    for acteur in depasses:
        audit.enregistrer_evenement(
            "alerte_volume_lecture",
            acteur.acteur_id,
            acteur.acteur_id,
            {
                "nombre_lectures": acteur.nombre_lectures,
                "fenetre_heures": FENETRE.total_seconds() / 3600,
                "seuil": SEUIL_LECTURES,
            },
        )
    return depasses


def _main() -> None:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--essai-a-blanc",
        action="store_true",
        help="Detecte et affiche sans ecrire d'alerte dans journal_audit.",
    )
    arguments = analyseur.parse_args()
    logging.basicConfig(level=logging.INFO)
    depasses = alert(arguments.essai_a_blanc)
    if not depasses:
        logger.info("Aucun acteur au-dessus du seuil (%d lectures/%s).", SEUIL_LECTURES, FENETRE)
        return
    for acteur in depasses:
        logger.warning(
            "acteur=%s nombre_lectures=%d (seuil=%d, fenetre=%s)%s",
            acteur.acteur_id,
            acteur.nombre_lectures,
            SEUIL_LECTURES,
            FENETRE,
            " [essai a blanc, rien ecrit]" if arguments.essai_a_blanc else "",
        )


if __name__ == "__main__":
    _main()
