"""Catalogue unique des variables autorisees pour le SOCLE."""

from dataclasses import dataclass
from typing import Literal

TypeFeature = Literal["continue", "nominale", "ordinale"]


@dataclass(frozen=True)
class FeatureSpec:
    code: str
    libelle: str
    type_ebm: TypeFeature
    explication: str


FEATURES_SOCLE: tuple[FeatureSpec, ...] = (
    FeatureSpec("anciennete_societaire_mois", "Anciennete de sociétariat", "continue", "Mois depuis l'adhésion."),
    FeatureSpec("nb_personnes_a_charge", "Personnes a charge", "continue", "Nombre déclaré par le sociétaire."),
    FeatureSpec("zone_residence", "Zone de residence", "nominale", "Zone déclarée du sociétaire."),
    FeatureSpec("parts_sociales_montant", "Parts sociales", "continue", "Montant des parts souscrites."),
    FeatureSpec("revenu_mensuel_declare", "Revenu mensuel declare", "continue", "Revenu déclaré, éventuellement absent."),
    FeatureSpec("ratio_endettement", "Ratio d'endettement", "continue", "Mensualité estimée du nouveau crédit divisée par le revenu."),
    FeatureSpec("duree_demandee_mois", "Duree demandee", "continue", "Durée contractuelle sollicitée."),
    FeatureSpec("solde_epargne_moyen_6m", "Epargne moyenne sur 6 mois", "continue", "Moyenne des six mois complets observables."),
    FeatureSpec("nb_mois_avec_depot_12m", "Regularite des depots", "continue", "Mois avec au moins un dépôt sur les douze derniers mois complets."),
    FeatureSpec("tendance_epargne_12m", "Tendance de l'epargne", "ordinale", "Erosion, stabilité ou hausse sur douze mois."),
    FeatureSpec("volatilite_epargne", "Volatilite de l'epargne", "continue", "Variabilité relative des mouvements d'épargne."),
    FeatureSpec("ratio_epargne_revenu", "Ratio epargne / revenu", "continue", "Epargne moyenne divisée par le revenu déclaré."),
    FeatureSpec("anciennete_epargne_mois", "Anciennete de l'epargne", "continue", "Mois entre ouverture et date de référence."),
    FeatureSpec("ratio_epargne_montant", "Capacite d'epargne rapportee au montant", "continue", "Epargne moyenne divisée par le montant demandé."),
    FeatureSpec("nb_credits_anterieurs", "Credits anterieurs", "continue", "Crédits débloqués avant la demande."),
    FeatureSpec("nb_incidents_anterieurs", "Incidents anterieurs", "continue", "Crédits antérieurs avec un retard observable d'au moins 30 jours."),
    FeatureSpec("max_jours_retard_historique", "Retard historique maximal", "continue", "Pire retard déjà observable ; absent pour un primo-emprunteur."),
    FeatureSpec("montant_max_rembourse", "Montant maximal correctement rembourse", "continue", "Plus gros crédit intégralement remboursé sans incident connu."),
    FeatureSpec("numero_cycle", "Cycle de credit", "continue", "Rang du crédit demandé dans l'historique."),
    FeatureSpec("ratio_montant_historique", "Ratio montant / historique", "continue", "Montant demandé divisé par le plus gros montant correctement remboursé."),
)

ORDRE_TENDANCE = ("erosion", "stable", "hausse")
COLONNES_AUDIT = ("credit_id", "societaire_id", "date_reference", "classe_cible", "cible", "split")
COLONNES_INTERDITES = frozenset(
    {
        "age", "sexe", "statut_matrimonial", "segment", "gie_id", "groupe_id",
        "produit_id", "taux_annuel", "periodicite_remboursement", "statut", "defaut",
        "jours_retard_max", "nom_complet", "numero_membre", "caisse_id", "niveau_education",
        "type_garantie", "garantie_appelee", "charge_mensualisee",
    }
)


def codes_features_socle() -> list[str]:
    return [feature.code for feature in FEATURES_SOCLE]


def types_ebm(catalogue: tuple[FeatureSpec, ...] = FEATURES_SOCLE) -> list[object]:
    result: list[object] = []
    for feature in catalogue:
        if feature.type_ebm == "continue":
            result.append("continuous")
        elif feature.type_ebm == "nominale":
            result.append("nominal")
        else:
            result.append(list(ORDRE_TENDANCE))
    return result


# Variables de la couche solidaire : uniquement pour un crédit dont l'emprunteur est le
# groupe (garantie `caution_solidaire_gie` + `gie_id` renseigné), jamais pour une demande
# individuelle d'un membre — cf. `précision.txt` réponses 1, 16, 21, 33 et
# `docs-solida/decisions-couche-solidaire.md`. Absentes (mises à `null`) si le groupe compte
# moins de `SEUIL_TAILLE_GROUPE_JUGEABLE` membres actifs (réponse 22).
SEUIL_TAILLE_GROUPE_JUGEABLE = 5

FEATURES_GROUPE: tuple[FeatureSpec, ...] = (
    FeatureSpec(
        "taille_groupe",
        "Taille du groupe",
        "continue",
        "Membres actifs (entrés, non sortis) à la date de référence.",
    ),
    FeatureSpec(
        "anciennete_groupe_mois",
        "Anciennete du groupe",
        "continue",
        "Mois depuis la création du GIE.",
    ),
    FeatureSpec(
        "nb_credits_groupe_anterieurs",
        "Credits de groupe anterieurs",
        "continue",
        "Crédits du même GIE débloqués avant la date de référence.",
    ),
    FeatureSpec(
        "nb_incidents_groupe_anterieurs",
        "Incidents de groupe anterieurs",
        "continue",
        "Crédits de groupe antérieurs avec un retard groupe observable d'au moins 30 jours.",
    ),
    FeatureSpec(
        "max_jours_retard_groupe_6m",
        "Retard groupe sur 6 mois",
        "continue",
        "Pire retard groupe observable dans les 6 mois précédant la référence.",
    ),
    FeatureSpec(
        "nb_cautions_appelees_anterieures",
        "Cautions du groupe appelees",
        "continue",
        "Cautions solidaires appelées sur des crédits de groupe antérieurs déjà clos.",
    ),
)

FEATURES_ENRICHI: tuple[FeatureSpec, ...] = FEATURES_SOCLE + FEATURES_GROUPE


def codes_features_enrichi() -> list[str]:
    return [feature.code for feature in FEATURES_ENRICHI]


def catalogue_par_identifiant(identifiant: str) -> tuple[FeatureSpec, ...]:
    if identifiant == "solida-socle":
        return FEATURES_SOCLE
    if identifiant == "solida-enrichi":
        return FEATURES_ENRICHI
    raise ValueError(f"Identifiant de catalogue inconnu : {identifiant!r}.")
