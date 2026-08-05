from typing import Protocol


class DepotFichesArchivees(Protocol):
    """Métadonnées de l'archivage (le PDF lui-même est dans `DepotFiches`)."""

    def enregistrer(self, decision_id: str, chemin_objet: str, archive_par: str) -> str: ...
