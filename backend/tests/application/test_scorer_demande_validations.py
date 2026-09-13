from datetime import UTC, datetime

import pytest

from solida.application.use_cases.scorer_demande_validations import (
    PLAFOND_INSTITUTIONNEL_FCFA,
    valider_acces_agence,
    valider_duree_dans_bornes,
    valider_montant_sous_plafond_institutionnel,
    valider_pas_de_credit_en_cours,
    valider_pas_de_multi_octroi,
    valider_produit_catalogue,
    valider_societaire_trouve,
)
from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.entities.societaire import Societaire
from solida.domain.errors import (
    AccesRefuse,
    DureeDemandeeInvalide,
    MontantDemandeInvalide,
    ProduitIntrouvable,
    SocietaireIntrouvable,
    SurEndettement,
)


def _societaire(**overrides: object) -> Societaire:
    values: dict[str, object] = {
        "societaire_id": "SOC-1",
        "numero_membre": "100001",
        "nom_complet": "Test Societaire",
        "agence": "CAI-00",
        "date_adhesion": datetime(2020, 1, 1, tzinfo=UTC).date(),
        "anciennete_mois": 48,
        "segment": "individuel",
        "age": 35,
        "zone": "urbain",
        "nb_personnes_a_charge": 2,
        "niveau_instruction": None,
        "parts_sociales_montant": 10000,
        "revenu_mensuel_declare": 150000,
        "groupe_id": None,
        "a_credit_en_cours": False,
    }
    values.update(overrides)
    return Societaire(**values)  # type: ignore[arg-type]


def _produit(**overrides: object) -> ProduitCredit:
    values: dict[str, object] = {
        "produit_id": "PROD-1",
        "libelle": "Produit test",
        "type_garantie": "individuelle",
        "montant_min": 50000,
        "montant_max": 1000000,
        "duree_min_mois": 3,
        "duree_max_mois": 24,
        "taux_annuel": 0.18,
    }
    values.update(overrides)
    return ProduitCredit(**values)  # type: ignore[arg-type]


class _FakeDecisionRepository:
    def __init__(self, exists: bool) -> None:
        self._exists = exists

    def existe_decision_accordee_depuis(
        self, societaire_id: str, depuis: datetime, entree_actuelle: dict[str, object]
    ) -> bool:
        return self._exists


def test_valider_societaire_trouve_renvoie_le_societaire() -> None:
    societaire = _societaire()

    assert valider_societaire_trouve(societaire, "SOC-1") is societaire


def test_valider_societaire_trouve_leve_si_absent() -> None:
    with pytest.raises(SocietaireIntrouvable):
        valider_societaire_trouve(None, "SOC-1")


def test_valider_acces_agence_ok_si_meme_agence() -> None:
    valider_acces_agence(_societaire(agence="CAI-00"), "CAI-00")


def test_valider_acces_agence_ok_si_pas_de_cloisonnement() -> None:
    valider_acces_agence(_societaire(agence="CAI-00"), None)


def test_valider_acces_agence_leve_si_agence_differente() -> None:
    with pytest.raises(AccesRefuse):
        valider_acces_agence(_societaire(agence="CAI-00"), "CAI-07")


def test_valider_pas_de_credit_en_cours_ok_si_aucun_credit() -> None:
    valider_pas_de_credit_en_cours(_societaire(a_credit_en_cours=False), "SOC-1")


def test_valider_pas_de_credit_en_cours_leve_si_credit_en_cours() -> None:
    with pytest.raises(SurEndettement):
        valider_pas_de_credit_en_cours(_societaire(a_credit_en_cours=True), "SOC-1")


def test_valider_pas_de_multi_octroi_ok_si_aucune_decision_recente() -> None:
    valider_pas_de_multi_octroi(
        _FakeDecisionRepository(exists=False), "SOC-1", datetime.now(UTC), {}
    )


def test_valider_pas_de_multi_octroi_leve_si_decision_recente() -> None:
    with pytest.raises(SurEndettement):
        valider_pas_de_multi_octroi(
            _FakeDecisionRepository(exists=True), "SOC-1", datetime.now(UTC), {}
        )


def test_valider_montant_sous_plafond_institutionnel_accepte_la_limite() -> None:
    valider_montant_sous_plafond_institutionnel(PLAFOND_INSTITUTIONNEL_FCFA)


def test_valider_montant_sous_plafond_institutionnel_leve_si_depasse() -> None:
    with pytest.raises(MontantDemandeInvalide):
        valider_montant_sous_plafond_institutionnel(PLAFOND_INSTITUTIONNEL_FCFA + 1)


def test_valider_produit_catalogue_renvoie_le_produit() -> None:
    produit = _produit()

    assert valider_produit_catalogue([produit], "PROD-1") is produit


def test_valider_produit_catalogue_leve_si_absent() -> None:
    with pytest.raises(ProduitIntrouvable):
        valider_produit_catalogue([], "PROD-1")


def test_valider_duree_dans_bornes_ok_si_dans_les_bornes() -> None:
    valider_duree_dans_bornes(12, _produit(duree_min_mois=3, duree_max_mois=24))


def test_valider_duree_dans_bornes_leve_si_hors_bornes() -> None:
    with pytest.raises(DureeDemandeeInvalide):
        valider_duree_dans_bornes(36, _produit(duree_min_mois=3, duree_max_mois=24))
