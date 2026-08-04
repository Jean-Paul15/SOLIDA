from solida.domain.rules.cascade import ContexteCascade, ParametresCascade, determiner_mode
from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.motif_bascule import MotifBascule

PARAMETRES = ParametresCascade()


def contexte_valide(**overrides: object) -> ContexteCascade:
    valeurs: dict[str, object] = {
        "appartient_a_un_groupe": True,
        "taille_groupe": 5,
        "nb_credits_anterieurs_groupe_soldes": 4,
        "fraicheur_features_jours": 1,
    }
    valeurs.update(overrides)
    return ContexteCascade(**valeurs)  # type: ignore[arg-type]


def test_les_quatre_conditions_reunies_donnent_le_mode_enrichi() -> None:
    resultat = determiner_mode(contexte_valide(), PARAMETRES)

    assert resultat.mode == ModeCalcul.ENRICHI
    assert resultat.motif is None


def test_sans_groupe_bascule_en_mode_socle_avec_le_motif_sans_groupe() -> None:
    resultat = determiner_mode(contexte_valide(appartient_a_un_groupe=False), PARAMETRES)

    assert resultat.mode == ModeCalcul.SOCLE_SEUL
    assert resultat.motif == MotifBascule.SANS_GROUPE


def test_un_groupe_trop_petit_bascule_en_mode_socle() -> None:
    resultat = determiner_mode(contexte_valide(taille_groupe=2), PARAMETRES)

    assert resultat.mode == ModeCalcul.SOCLE_SEUL
    assert resultat.motif == MotifBascule.GROUPE_TROP_PETIT


def test_un_groupe_sans_historique_suffisant_bascule_en_mode_socle() -> None:
    resultat = determiner_mode(contexte_valide(nb_credits_anterieurs_groupe_soldes=1), PARAMETRES)

    assert resultat.mode == ModeCalcul.SOCLE_SEUL
    assert resultat.motif == MotifBascule.GROUPE_SANS_HISTORIQUE


def test_des_features_absentes_bascule_en_mode_socle() -> None:
    resultat = determiner_mode(contexte_valide(fraicheur_features_jours=None), PARAMETRES)

    assert resultat.mode == ModeCalcul.SOCLE_SEUL
    assert resultat.motif == MotifBascule.FEATURES_PERIMEES


def test_des_features_trop_vieilles_bascule_en_mode_socle() -> None:
    resultat = determiner_mode(contexte_valide(fraicheur_features_jours=7), PARAMETRES)

    assert resultat.mode == ModeCalcul.SOCLE_SEUL
    assert resultat.motif == MotifBascule.FEATURES_PERIMEES
