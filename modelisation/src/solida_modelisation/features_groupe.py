"""Couche solidaire : agrégats du groupe emprunteur, calculés sans regarder le futur.

Un crédit de groupe est un crédit dont l'emprunteur officiel est le GIE (garantie
`caution_solidaire_gie` et `gie_id` renseigné) — `précision.txt` réponses 1 à 3. Ces
agrégats décrivent alors les antécédents **du groupe emprunteur lui-même**, jamais ceux
d'un autre membre : les réponses 21 et 33 excluent explicitement qu'un membre voie son
score influencé par le comportement d'un tiers du groupe. Une demande individuelle
(hors crédit de groupe) ne calcule donc aucune de ces variables.

Fonctions pures, sans pandas : elles opèrent sur des enregistrements simples pour être
appelées à l'identique depuis le pipeline d'entraînement (pandas) et depuis le feature
store d'inférence du backend (SQLAlchemy), garantissant la parité J2-08b par
construction plutôt que par duplication de logique.
"""

from dataclasses import dataclass
from datetime import date

from .catalogue import SEUIL_TAILLE_GROUPE_JUGEABLE


@dataclass(frozen=True)
class AppartenanceGie:
    societaire_id: str
    date_entree: date
    date_sortie: date | None


@dataclass(frozen=True)
class CreditGroupeAnterieur:
    credit_id: str
    date_deblocage: date
    date_issue: date | None
    statut: str = "solde"
    """`solde` | `en_cours` | `en_souffrance`. Valeur par défaut neutre pour les usages qui
    n'en ont pas besoin (`calculer_features_groupe` l'ignore) ; le backend l'utilise pour
    décider de l'éligibilité au mode enrichi (cascade), le pipeline d'entraînement pour le
    jeu historique où le statut est toujours connu."""


@dataclass(frozen=True)
class EcheanceGroupe:
    credit_id: str
    date_paiement_reelle: date | None
    jours_retard: float | None


@dataclass(frozen=True)
class CautionGroupe:
    credit_id: str
    garantie_appelee: bool


@dataclass(frozen=True)
class FeaturesGroupe:
    """`None` sur chaque champ si le groupe compte moins de membres que le seuil jugeable."""

    taille_groupe: int
    anciennete_groupe_mois: int | None
    nb_credits_groupe_anterieurs: int | None
    nb_incidents_groupe_anterieurs: int | None
    max_jours_retard_groupe_6m: float | None
    nb_cautions_appelees_anterieures: int | None


def _mois_ecoules(debut: date, fin: date) -> int:
    """Nombre de mois révolus entre deux dates, borné à zéro."""
    valeur = (fin.year - debut.year) * 12 + fin.month - debut.month
    if fin.day < debut.day:
        valeur -= 1
    return max(valeur, 0)


def _mois_avant(reference: date, nb_mois: int) -> date:
    """Date correspondant à `reference` moins `nb_mois` mois pleins."""
    mois_total = reference.month - 1 - nb_mois
    annee = reference.year + mois_total // 12
    mois = mois_total % 12 + 1
    jour = min(reference.day, 28)
    return date(annee, mois, jour)


def taille_groupe_a_date(appartenances: list[AppartenanceGie], date_reference: date) -> int:
    """Membres entrés avant la référence et non encore sortis à cette date."""
    return sum(
        1
        for appartenance in appartenances
        if appartenance.date_entree <= date_reference
        and (appartenance.date_sortie is None or appartenance.date_sortie > date_reference)
    )


def calculer_features_groupe(
    date_reference: date,
    date_creation_groupe: date,
    appartenances: list[AppartenanceGie],
    credits_anterieurs: list[CreditGroupeAnterieur],
    echeances_groupe: list[EcheanceGroupe],
    cautions_anterieures: list[CautionGroupe],
    seuil_taille_minimale: int = SEUIL_TAILLE_GROUPE_JUGEABLE,
) -> FeaturesGroupe:
    """Agrège l'historique du groupe emprunteur, strictement antérieur à `date_reference`.

    `credits_anterieurs`, `echeances_groupe` et `cautions_anterieures` doivent déjà être
    filtrés par l'appelant sur le même `gie_id` que le crédit évalué ; cette fonction ne
    fait que vérifier la borne temporelle, jamais la sélection du groupe.
    """
    taille = taille_groupe_a_date(appartenances, date_reference)
    if taille < seuil_taille_minimale:
        return FeaturesGroupe(
            taille_groupe=taille,
            anciennete_groupe_mois=None,
            nb_credits_groupe_anterieurs=None,
            nb_incidents_groupe_anterieurs=None,
            max_jours_retard_groupe_6m=None,
            nb_cautions_appelees_anterieures=None,
        )

    precedents = [c for c in credits_anterieurs if c.date_deblocage < date_reference]
    identifiants_precedents = {credit.credit_id for credit in precedents}

    observees = [
        echeance
        for echeance in echeances_groupe
        if echeance.credit_id in identifiants_precedents
        and echeance.date_paiement_reelle is not None
        and echeance.date_paiement_reelle <= date_reference
    ]
    retards_par_credit: dict[str, float] = {}
    for echeance in observees:
        retard = echeance.jours_retard or 0.0
        retards_par_credit[echeance.credit_id] = max(
            retards_par_credit.get(echeance.credit_id, 0.0), retard
        )
    nb_incidents = sum(1 for retard in retards_par_credit.values() if retard >= 30)

    debut_fenetre = _mois_avant(date_reference, 6)
    observees_fenetre = [
        echeance
        for echeance in observees
        if echeance.date_paiement_reelle is not None
        and debut_fenetre <= echeance.date_paiement_reelle <= date_reference
    ]
    retards_fenetre = [echeance.jours_retard or 0.0 for echeance in observees_fenetre]
    max_retard_6m = max(retards_fenetre) if retards_fenetre else None

    # `garanties` ne date pas l'appel de caution : seule une caution sur un crédit déjà
    # clos (`date_issue` connue et passée) est traitée comme un événement antérieur.
    credits_clos = {
        credit.credit_id
        for credit in precedents
        if credit.date_issue is not None and credit.date_issue <= date_reference
    }
    nb_cautions_appelees = sum(
        1
        for caution in cautions_anterieures
        if caution.credit_id in credits_clos and caution.garantie_appelee
    )

    return FeaturesGroupe(
        taille_groupe=taille,
        anciennete_groupe_mois=_mois_ecoules(date_creation_groupe, date_reference),
        nb_credits_groupe_anterieurs=len(precedents),
        nb_incidents_groupe_anterieurs=nb_incidents,
        max_jours_retard_groupe_6m=max_retard_6m,
        nb_cautions_appelees_anterieures=nb_cautions_appelees,
    )
