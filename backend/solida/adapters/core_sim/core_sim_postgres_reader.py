from datetime import date

from solida_modelisation.features_epargne import SoldeMensuelEpargne
from sqlalchemy import Engine

from solida.adapters.core_sim.postgres_credit_reader import PostgresCreditReader
from solida.adapters.core_sim.postgres_donnees_groupe_reader import PostgresDonneesGroupeReader
from solida.adapters.core_sim.postgres_epargne_reader import PostgresEpargneReader
from solida.adapters.core_sim.postgres_garantie_reader import PostgresGarantieReader
from solida.adapters.core_sim.postgres_groupe_reader import PostgresGroupeReader
from solida.adapters.core_sim.postgres_produit_reader import PostgresProduitReader
from solida.adapters.core_sim.postgres_societaire_reader import PostgresSocietaireReader
from solida.adapters.core_sim.postgres_solde_mensuel_reader import PostgresSoldeMensuelReader
from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.credit import Credit
from solida.domain.entities.garantie import Garantie
from solida.domain.entities.groupe import GroupeCaution
from solida.domain.entities.mouvement_epargne import MouvementEpargne
from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.entities.societaire import Societaire
from solida.domain.values.features import DonneesGroupeBrutes
from solida.domain.values.societaire_search_result import SocietaireSearchResult


class CoreSimPostgresReader:
    """Implémentation du port `CoreSimReader` contre le schéma réel produit par
    `simulateur/`. Connexion via le rôle `solida_lecteur` (lecture seule).

    Façade qui délègue chaque sous-domaine (société, crédit, épargne, garantie, groupe,
    produit) à un composant de lecture interne dédié — le port reste une interface unique, seule
    l'implémentation est scindée (voir docs/backend/01-adapters-core-sim.md).
    """

    def __init__(self, engine: Engine) -> None:
        self._societaires = PostgresSocietaireReader(engine)
        self._credits = PostgresCreditReader(engine)
        self._epargne = PostgresEpargneReader(engine)
        self._garanties = PostgresGarantieReader(engine)
        self._groupes = PostgresGroupeReader(engine)
        self._produits = PostgresProduitReader(engine)
        self._donnees_groupe = PostgresDonneesGroupeReader(engine)
        self._soldes_mensuels = PostgresSoldeMensuelReader(engine)

    def rechercher_societaires(
        self, terme: str, limite: int, agence_id: str | None = None
    ) -> list[SocietaireSearchResult]:
        return self._societaires.rechercher_societaires(terme, limite, agence_id)

    def compter_societaires(self, terme: str, agence_id: str | None = None) -> int:
        return self._societaires.compter_societaires(terme, agence_id)

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        return self._societaires.charger_societaire(societaire_id)

    def charger_societaire_par_numero_membre(self, numero_membre: str) -> Societaire | None:
        return self._societaires.charger_societaire_par_numero_membre(numero_membre)

    def charger_historique_credit(self, societaire_id: str) -> list[Credit]:
        return self._credits.charger_historique_credit(societaire_id)

    def charger_compte_epargne(self, societaire_id: str) -> CompteEpargne | None:
        return self._epargne.charger_compte_epargne(societaire_id)

    def charger_mouvements_epargne(
        self, societaire_id: str, depuis: date
    ) -> list[MouvementEpargne]:
        return self._epargne.charger_mouvements_epargne(societaire_id, depuis)

    def charger_groupe(self, societaire_id: str) -> GroupeCaution | None:
        return self._groupes.charger_groupe(societaire_id)

    def charger_garanties(self, societaire_id: str) -> list[Garantie]:
        return self._garanties.charger_garanties(societaire_id)

    def charger_produits(self) -> list[ProduitCredit]:
        return self._produits.charger_produits()

    def charger_donnees_groupe(self, gie_id: str) -> DonneesGroupeBrutes | None:
        return self._donnees_groupe.charger_donnees_groupe(gie_id)

    def charger_soldes_mensuels(self, societaire_id: str, avant: date) -> list[SoldeMensuelEpargne]:
        return self._soldes_mensuels.charger_soldes_mensuels(societaire_id, avant)
