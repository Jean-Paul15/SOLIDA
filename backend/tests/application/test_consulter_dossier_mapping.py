from datetime import date

from solida.application.use_cases.consulter_dossier_mapping import (
    _alertes,
    _groupe_affiche,
    _ratio_epargne_revenu,
    _secteur,
)
from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.groupe import GroupeCaution, MembreGroupe
from solida.domain.values.dossier import CreditResume


def _membre(**overrides: object) -> MembreGroupe:
    valeurs: dict[str, object] = {
        "societaire_id": "SOC-2",
        "nom_complet": "Membre Groupe",
        "role": "membre",
        "anciennete_mois": 24,
        "statut_credit": "en_cours",
        "caution_appelee": False,
    }
    valeurs.update(overrides)
    return MembreGroupe(**valeurs)  # type: ignore[arg-type]


def _groupe(**overrides: object) -> GroupeCaution:
    valeurs: dict[str, object] = {
        "groupe_id": "GRP-1",
        "nom_groupe": "Groupe Test",
        "taille_actuelle": 5,
        "date_creation": date(2019, 1, 1),
        "taux_remboursement_groupe": 0.95,
        "nb_cycles_completes": 3,
        "nb_credits_anterieurs_soldes": 10,
        "nb_sorties_12m": 0,
        "statut": "actif",
        "membres": [_membre()],
    }
    valeurs.update(overrides)
    return GroupeCaution(**valeurs)  # type: ignore[arg-type]


# --- _secteur ---


def test_secteur_connu_pour_chaque_segment() -> None:
    assert _secteur("agricole") == "Agriculture"
    assert _secteur("salarie") == "Salariat"
    assert _secteur("individuel") == "Commerce et services"
    assert _secteur("jeune") == "Activité en démarrage"
    assert _secteur("femme_gie") == "Commerce (groupement)"


def test_secteur_segment_inconnu_renvoie_le_defaut() -> None:
    assert _secteur("segment_inexistant") == "Non renseigné"


# --- _groupe_affiche ---


def test_groupe_affiche_none_renvoie_none() -> None:
    assert _groupe_affiche(None) is None


def test_groupe_affiche_convertit_le_groupe_et_ses_membres() -> None:
    affiche = _groupe_affiche(_groupe())

    assert affiche is not None
    assert affiche.groupe_id == "GRP-1"
    assert affiche.statut == "actif"
    assert len(affiche.membres) == 1
    assert affiche.membres[0].societaire_id == "SOC-2"


# --- _alertes ---


def test_alertes_vide_sans_credit_en_souffrance_ni_groupe() -> None:
    assert _alertes([], None) == []


def test_alertes_signale_un_credit_en_souffrance() -> None:
    historique = [
        CreditResume(
            credit_id="CR-1",
            produit_id="PROD-1",
            date_deblocage=date(2023, 1, 1),
            montant_octroye=200000,
            duree_mois=12,
            numero_cycle=1,
            statut="en_souffrance",
            capital_restant_du=50000,
            max_jours_retard=45,
        )
    ]

    alertes = _alertes(historique, None)

    assert "Un crédit en souffrance figure dans l'historique." in alertes


def test_alertes_signale_un_groupe_en_difficulte() -> None:
    groupe_affiche = _groupe_affiche(_groupe(statut="en_difficulte"))

    alertes = _alertes([], groupe_affiche)

    assert "Le groupe de caution est en difficulté." in alertes


def test_alertes_signale_une_caution_deja_appelee() -> None:
    groupe_affiche = _groupe_affiche(_groupe(membres=[_membre(caution_appelee=True)]))

    alertes = _alertes([], groupe_affiche)

    assert "Une caution a déjà été appelée dans le groupe." in alertes


# --- _ratio_epargne_revenu ---


def test_ratio_epargne_revenu_sans_compte_est_nul() -> None:
    assert _ratio_epargne_revenu(None, 100000) == 0.0


def test_ratio_epargne_revenu_avec_revenu_nul_est_nul() -> None:
    compte = CompteEpargne(
        compte_id="CPT-1",
        societaire_id="SOC-1",
        solde_moyen_6m=50000,
        nb_mois_avec_depot_12m=10,
        croissance_12m=0.1,
        volatilite=0.2,
    )

    assert _ratio_epargne_revenu(compte, None) == 0.0
    assert _ratio_epargne_revenu(compte, 0) == 0.0


def test_ratio_epargne_revenu_est_borne_a_5() -> None:
    compte = CompteEpargne(
        compte_id="CPT-1",
        societaire_id="SOC-1",
        solde_moyen_6m=1_000_000,
        nb_mois_avec_depot_12m=10,
        croissance_12m=0.1,
        volatilite=0.2,
    )

    assert _ratio_epargne_revenu(compte, 10_000) == 5.0
