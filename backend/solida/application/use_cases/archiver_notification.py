from dataclasses import dataclass

from solida.domain.errors import AccesRefuse
from solida.domain.ports.demande_societaire import DemandeSocietaireRepository
from solida.domain.values.demande_societaire import DemandeSocietaire


@dataclass(frozen=True)
class ArchiverNotification:
    demande_societaire_repository: DemandeSocietaireRepository

    def execute(
        self, demande_id: str, agent_id: str, agent_agence_id: str | None
    ) -> DemandeSocietaire | None:
        demande = self.demande_societaire_repository.lire(demande_id)
        if demande is None:
            return None
        if agent_agence_id is not None and demande.agence_id != agent_agence_id:
            raise AccesRefuse("Cette demande ne concerne pas votre agence.")
        return self.demande_societaire_repository.archiver(demande_id, agent_id)
