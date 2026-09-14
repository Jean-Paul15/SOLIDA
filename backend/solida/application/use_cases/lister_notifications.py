from dataclasses import dataclass

from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.demande_societaire import DemandeSocietaireRepository
from solida.domain.values.demande_societaire import STATUT_NOUVELLE, DemandeSocietaireAffichee


@dataclass(frozen=True)
class ListerNotifications:
    demande_societaire_repository: DemandeSocietaireRepository
    core_sim_reader: CoreSimReader

    def execute(
        self, role: str, agent_id: str, agence_id: str | None, limite: int, decalage: int
    ) -> tuple[list[DemandeSocietaireAffichee], int]:
        """Un superviseur voit les demandes non assignées de son périmètre (à répartir) ; un
        agent ne voit que celles qui lui ont été assignées (fin de la boîte partagée)."""
        if role == "superviseur":
            demandes = self.demande_societaire_repository.lister_non_assignees(
                agence_id, STATUT_NOUVELLE, limite, decalage
            )
            total = self.demande_societaire_repository.compter_non_assignees(
                agence_id, STATUT_NOUVELLE
            )
        else:
            demandes = self.demande_societaire_repository.lister_assignees(
                agence_id, agent_id, STATUT_NOUVELLE, limite, decalage
            )
            total = self.demande_societaire_repository.compter_assignees(
                agence_id, agent_id, STATUT_NOUVELLE
            )

        affichees = []
        for demande in demandes:
            societaire = self.core_sim_reader.charger_societaire(demande.societaire_id)
            nom = societaire.nom_complet if societaire is not None else "Sociétaire introuvable"
            affichees.append(DemandeSocietaireAffichee(demande=demande, societaire_nom=nom))
        return affichees, total
