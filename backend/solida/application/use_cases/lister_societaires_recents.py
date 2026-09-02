from dataclasses import dataclass

from solida.domain.ports.audit import AuditLog
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.values.societaire_search_result import SocietaireSearchResult

TYPE_EVENEMENT_CONSULTATION = "consultation_dossier"
LIMITE_PAR_DEFAUT = 5


@dataclass(frozen=True)
class ListerSocietairesRecents:
    """Réutilise le journal d'audit plutôt qu'une table de récents dédiée."""

    core_sim_reader: CoreSimReader
    audit_log: AuditLog

    def execute(
        self, agent_id: str, limite: int = LIMITE_PAR_DEFAUT
    ) -> list[SocietaireSearchResult]:
        identifiants = self.audit_log.lister_objets_recents(
            TYPE_EVENEMENT_CONSULTATION, agent_id, limite
        )
        search_results = []
        for societaire_id in identifiants:
            societaire = self.core_sim_reader.charger_societaire(societaire_id)
            if societaire is None:
                continue
            credits = self.core_sim_reader.charger_historique_credit(societaire_id)
            search_results.append(
                SocietaireSearchResult(
                    societaire_id=societaire.societaire_id,
                    nom_complet=societaire.nom_complet,
                    numero_membre=societaire.numero_membre,
                    agence=societaire.agence,
                    zone=societaire.zone,
                    statut="actif",
                    a_credit_en_cours=any(c.statut == "en_cours" for c in credits),
                )
            )
        return search_results
