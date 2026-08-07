import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class FormateurJSON(logging.Formatter):
    """Une ligne JSON par entrée, horodatée en UTC explicite — format standard pour
    l'ingestion par un collecteur de logs (Loki, CloudWatch, ELK...), sans dépendance
    supplémentaire : seul le module `json` de la bibliothèque standard est utilisé."""

    def format(self, enregistrement: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "horodatage": datetime.fromtimestamp(enregistrement.created, tz=UTC).isoformat(),
            "niveau": enregistrement.levelname,
            "logger": enregistrement.name,
            "message": enregistrement.getMessage(),
        }
        payload.update(getattr(enregistrement, "champs", {}))
        if enregistrement.exc_info:
            payload["exception"] = self.formatException(enregistrement.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configurer_journalisation() -> None:
    """Journalisation applicative sur stdout, en JSON structuré — capturée par `docker
    logs`, pas de service externe : cohérent avec la contrainte de légèreté du projet.
    Le journal d'audit métier (`journal_audit`, en base) est distinct et complémentaire,
    pas remplacé par ceci. Ne couvre pas le logger interne d'uvicorn (bannière de
    démarrage, tracebacks non gérés) : celui-ci a ses propres handlers, isolés du logger
    racine (`propagate=False`), donc hors de portée d'une reconfiguration ici."""
    gestionnaire = logging.StreamHandler(sys.stdout)
    gestionnaire.setFormatter(FormateurJSON())
    logging.basicConfig(level=logging.INFO, handlers=[gestionnaire], force=True)
