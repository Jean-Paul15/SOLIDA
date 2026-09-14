from dataclasses import dataclass

from solida.domain.errors import AccesRefuse
from solida.domain.ports.demande_societaire import DemandeSocietaireRepository
from solida.domain.ports.utilisateurs import UtilisateurRepository
from solida.domain.values.demande_societaire import DemandeSocietaire


@dataclass(frozen=True)
class AssignerNotification:
    demande_societaire_repository: DemandeSocietaireRepository
    utilisateur_repository: UtilisateurRepository

    def execute(
        self, demande_id: str, superviseur_agence_id: str | None, agent_cible_id: str
    ) -> DemandeSocietaire | None:
        demande = self.demande_societaire_repository.lire(demande_id)
        if demande is None:
            return None
        if superviseur_agence_id is not None and demande.agence_id != superviseur_agence_id:
            raise AccesRefuse("Cette demande ne concerne pas votre agence.")

        agent_cible = self.utilisateur_repository.lire(agent_cible_id)
        if (
            agent_cible is None
            or agent_cible.role != "agent"
            or agent_cible.desactive_le is not None
        ):
            raise AccesRefuse("L'agent désigné est introuvable ou n'est pas un agent actif.")
        if agent_cible.agence_id != demande.agence_id:
            raise AccesRefuse("L'agent désigné n'appartient pas à l'agence de cette demande.")
        if demande.assigne_a_agent_id is not None:
            raise AccesRefuse("Cette demande est déjà assignée à un agent.")

        return self.demande_societaire_repository.assigner(demande_id, agent_cible_id)
