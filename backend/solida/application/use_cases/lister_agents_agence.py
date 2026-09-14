from dataclasses import dataclass

from solida.domain.ports.utilisateurs import UtilisateurRepository
from solida.domain.values.utilisateur import UtilisateurResume


@dataclass(frozen=True)
class ListerAgentsAgence:
    utilisateur_repository: UtilisateurRepository

    def execute(self, agence_id: str) -> list[UtilisateurResume]:
        return self.utilisateur_repository.lister_agents_agence(agence_id)
