from typing import Protocol


class DepotFiches(Protocol):
    """Stockage objet des fiches PDF archivées — jamais en base (`solida` reste léger)."""

    def archiver(self, chemin_objet: str, contenu: bytes) -> None: ...
