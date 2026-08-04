from dataclasses import dataclass

from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.values.resultat_recherche import ResultatRechercheSocietaire

LONGUEUR_MINIMALE_TERME = 2


@dataclass(frozen=True)
class RechercherSocietaire:
    lecteur: LecteurCoreSim

    def executer(
        self, terme: str, limite: int, agence_id: str | None
    ) -> list[ResultatRechercheSocietaire]:
        if len(terme) < LONGUEUR_MINIMALE_TERME:
            return []
        return self.lecteur.rechercher_societaires(terme, limite, agence_id)
