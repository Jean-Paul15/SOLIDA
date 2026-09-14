from typing import Protocol

from solida.domain.values.utilisateur import UtilisateurResume


class UtilisateurRepository(Protocol):
    def lire(self, utilisateur_id: str) -> UtilisateurResume | None: ...

    def lister_agents_agence(self, agence_id: str) -> list[UtilisateurResume]: ...
