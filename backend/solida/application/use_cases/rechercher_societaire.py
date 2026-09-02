from dataclasses import dataclass

from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.values.societaire_search_result import SocietaireSearchResult

LONGUEUR_MINIMALE_TERME = 2


@dataclass(frozen=True)
class RechercherSocietaire:
    core_sim_reader: CoreSimReader

    def execute(
        self, terme: str, limite: int, agence_id: str | None
    ) -> list[SocietaireSearchResult]:
        if len(terme) < LONGUEUR_MINIMALE_TERME:
            return []
        return self.core_sim_reader.rechercher_societaires(terme, limite, agence_id)

    def compter(self, terme: str, agence_id: str | None) -> int:
        if len(terme) < LONGUEUR_MINIMALE_TERME:
            return 0
        return self.core_sim_reader.compter_societaires(terme, agence_id)
