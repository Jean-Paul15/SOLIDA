from typing import Protocol


class FicheArchiveeRepository(Protocol):
    """Métadonnées de l'archivage (le PDF lui-même est dans `FicheRepository`)."""

    def enregistrer(self, decision_id: str, chemin_objet: str, archive_par: str) -> str: ...
