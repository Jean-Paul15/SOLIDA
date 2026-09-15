from datetime import date

from solida.application.use_cases.authenticate_societaire import _prenom
from solida.domain.entities.societaire import Societaire


def _societaire(nom_complet: str) -> Societaire:
    return Societaire(
        societaire_id="SOC-1",
        numero_membre="M-1",
        nom_complet=nom_complet,
        agence="CAI-00",
        date_adhesion=date(2020, 1, 1),
        anciennete_mois=48,
        segment="individuel",
        age=40,
        zone="urbaine",
        nb_personnes_a_charge=0,
        niveau_instruction=None,
        parts_sociales_montant=10000,
        revenu_mensuel_declare=None,
        groupe_id=None,
        a_credit_en_cours=False,
    )


def test_prenom_ignore_le_patronyme_place_en_premier() -> None:
    # Convention du générateur (simulateur/simulateur/pipeline.py::noms) : le patronyme
    # précède toujours le ou les prénoms, par ex. "KOSSIVI Afia Selom".
    assert _prenom(_societaire("KOSSIVI Afia Selom")) == "Afia"


def test_prenom_sans_second_prenom() -> None:
    assert _prenom(_societaire("SOSSOU Mawusi")) == "Mawusi"


def test_prenom_nom_complet_a_un_seul_mot() -> None:
    assert _prenom(_societaire("Afia")) == "Afia"
