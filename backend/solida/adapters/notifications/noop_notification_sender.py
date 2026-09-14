import logging

from solida.domain.values.demande_societaire import DemandeSocietaire

logger = logging.getLogger(__name__)


class NoopNotificationSender:
    """Canal externe reporté (email ou autre, décision explicite) : log seulement,
    remplacer par un vrai envoi quand le canal est choisi."""

    def notifier(self, demande: DemandeSocietaire) -> None:
        logger.info(
            "notification_demande_societaire agence=%s demande_id=%s",
            demande.agence_id,
            demande.demande_id,
        )
