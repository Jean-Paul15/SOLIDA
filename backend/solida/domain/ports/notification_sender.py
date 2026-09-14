from typing import Protocol

from solida.domain.values.demande_societaire import DemandeSocietaire


class NotificationSender(Protocol):
    """Canal externe (email ou autre, à définir) — reporté par décision explicite.
    L'implémentation actuelle (NoopNotificationSender) ne fait qu'un log."""

    def notifier(self, demande: DemandeSocietaire) -> None: ...
