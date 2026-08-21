import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Une ligne JSON par entrée, horodatée en UTC explicite — format standard pour
    l'ingestion par un collecteur de logs (Loki, CloudWatch, ELK...), sans dépendance
    supplémentaire : seul le module `json` de la bibliothèque standard est utilisé."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(getattr(record, "fields", {}))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> None:
    """Journalisation applicative sur stdout, en JSON structuré — capturée par `docker
    logs`, pas de service externe : cohérent avec la contrainte de légèreté du projet.
    Le journal d'audit métier (`journal_audit`, en base) est distinct et complémentaire,
    pas remplacé par ceci. Ne couvre pas le logger interne d'uvicorn (bannière de
    démarrage, tracebacks non gérés) : celui-ci a ses propres handlers, isolés du logger
    racine (`propagate=False`), donc hors de portée d'une reconfiguration ici."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
