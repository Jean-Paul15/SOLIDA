"""Couvre en particulier les codes de la couche solidaire (J2-08b) et
`tendance_epargne_12m`, ajoutés au catalogue de features après la première rédaction de
`libelles_variables.py` — sans ce test, un nouveau code de feature peut redevenir
« Variable non documentée » à l'écran sans qu'aucun test ne le signale."""

from solida.adapters.http.libelles_variables import famille, formater_valeur, libelle

CODES_COUCHE_SOLIDAIRE = [
    "taille_groupe",
    "anciennete_groupe_mois",
    "nb_credits_groupe_anterieurs",
    "nb_incidents_groupe_anterieurs",
    "max_jours_retard_groupe_6m",
    "nb_cautions_appelees_anterieures",
]


def test_chaque_code_de_la_couche_solidaire_a_un_libelle_documente() -> None:
    for code in CODES_COUCHE_SOLIDAIRE:
        assert libelle(code) != "Variable non documentée", code
        assert famille(code) == "solidaire"


def test_tendance_epargne_12m_a_un_libelle_documente() -> None:
    assert libelle("tendance_epargne_12m") != "Variable non documentée"


def test_tendance_epargne_12m_traduit_les_trois_valeurs_connues() -> None:
    assert formater_valeur("tendance_epargne_12m", "hausse") == "En hausse"
    assert formater_valeur("tendance_epargne_12m", "stable") == "Stable"
    assert formater_valeur("tendance_epargne_12m", "erosion") == "En érosion"


def test_code_inconnu_reste_signale_explicitement() -> None:
    assert libelle("un_code_qui_nexiste_pas") == "Variable non documentée"
