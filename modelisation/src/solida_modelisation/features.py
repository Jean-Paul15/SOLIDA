"""Features SOCLE calculées sans regarder le futur du crédit évalué."""

import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from .catalogue import ORDRE_TENDANCE, codes_features_enrichi, codes_features_socle
from .cible import construire_cible
from .features_epargne import SoldeMensuelEpargne, calculer_features_epargne
from .features_groupe import (
    AppartenanceGie,
    CautionGroupe,
    CreditGroupeAnterieur,
    EcheanceGroupe,
    calculer_features_groupe,
)
from .finance import mensualite_actuarielle
from .splits import attribuer_split


@dataclass(frozen=True)
class TablesBrutes:
    societaires: pd.DataFrame
    credits: pd.DataFrame
    echeances: pd.DataFrame
    soldes_mensuels: pd.DataFrame
    produits: pd.DataFrame


@dataclass(frozen=True)
class TablesGroupe:
    """Tables supplémentaires nécessaires à la couche solidaire (modèle enrichi)."""

    appartenances: pd.DataFrame
    groupes_gie: pd.DataFrame
    garanties: pd.DataFrame


def lire_tables_brutes(dossier: Path) -> TablesBrutes:
    """Lit les seules tables nécessaires au SOCLE depuis une sortie du simulateur."""
    return TablesBrutes(
        societaires=pd.read_parquet(dossier / "societaires.parquet"),
        credits=pd.read_parquet(dossier / "credits.parquet"),
        echeances=pd.read_parquet(dossier / "echeances.parquet"),
        soldes_mensuels=pd.read_parquet(dossier / "solde_mensuel_epargne.parquet"),
        produits=pd.read_parquet(dossier / "produits_credit.parquet"),
    )


def lire_tables_groupe(dossier: Path) -> TablesGroupe:
    """Lit les tables de la couche solidaire depuis une sortie du simulateur."""
    return TablesGroupe(
        appartenances=pd.read_parquet(dossier / "appartenances_gie.parquet"),
        groupes_gie=pd.read_parquet(dossier / "groupes_gie.parquet"),
        garanties=pd.read_parquet(dossier / "garanties.parquet"),
    )


def mois_ecoules(debut: pd.Timestamp, fin: pd.Timestamp) -> int:
    """Nombre de mois révolus entre deux dates, borné à zéro."""
    valeur = (fin.year - debut.year) * 12 + fin.month - debut.month
    if fin.day < debut.day:
        valeur -= 1
    return max(valeur, 0)


def _tranche_montant(montant: float) -> str:
    if montant < 100_000:
        return "moins_100k"
    if montant < 500_000:
        return "100k_500k"
    if montant < 1_000_000:
        return "500k_1m"
    return "1m_ou_plus"


def _nombre(valeur: object, colonne: str) -> float:
    """Convertit une valeur scalaire attendue et échoue clairement sinon."""
    if isinstance(valeur, (int, float, np.integer, np.floating)) and not isinstance(valeur, bool):
        return float(valeur)
    raise TypeError(f"La colonne {colonne} doit contenir un nombre, reçu {valeur!r}.")


def _nombre_optionnel(valeur: object, colonne: str) -> float | None:
    if valeur is None or valeur is pd.NA:
        return None
    if isinstance(valeur, (float, np.floating)) and math.isnan(float(valeur)):
        return None
    return _nombre(valeur, colonne)


def _features_epargne(soldes: pd.DataFrame, date_reference: pd.Timestamp) -> dict[str, float | int | str]:
    """Utilise seulement des mois totalement clos avant la date de référence.

    Fine couche pandas -> objets purs autour de `calculer_features_epargne` : le calcul
    lui-même vit dans `features_epargne.py`, partagé à l'identique par le backend (J2-11,
    parité entraînement/inférence).
    """
    lignes = [
        SoldeMensuelEpargne(
            mois=pd.Timestamp(ligne["mois"]).date(),
            solde_fin_mois=float(ligne["solde_fin_mois"]),
            total_depots=float(ligne["total_depots"]),
        )
        for ligne in soldes.to_dict("records")
    ]
    resultat = calculer_features_epargne(lignes, date_reference.date())
    return {
        "solde_epargne_moyen_6m": resultat.solde_epargne_moyen_6m,
        "nb_mois_avec_depot_12m": resultat.nb_mois_avec_depot_12m,
        "tendance_epargne_12m": resultat.tendance_epargne_12m,
        "volatilite_epargne": resultat.volatilite_epargne,
    }


def _historique_observable(
    credit: pd.Series,
    credits_societaire: pd.DataFrame,
    echeances: pd.DataFrame,
    *,
    niveau_individuel_seulement: bool = False,
) -> dict[str, float | int]:
    """Construit l'historique avec les seuls paiements réellement connus à la date donnée.

    `niveau_individuel_seulement` (jeu enrichi uniquement) exclut les échéances
    enregistrées au niveau du groupe : pour un crédit dont le remboursement est collecté
    collectivement, le retard individuel n'existe pas dans les données (5.10), il ne doit
    donc jamais être fabriqué comme un zéro. Le nombre de crédits antérieurs et le numéro
    de cycle restent comptés sans ce filtre : ils décrivent le parcours du sociétaire, pas
    son comportement de paiement.
    """
    reference = pd.Timestamp(credit["date_deblocage"])
    precedents = credits_societaire[
        pd.to_datetime(credits_societaire["date_deblocage"]) < reference
    ].copy()
    if precedents.empty:
        return {
            "nb_credits_anterieurs": 0,
            "nb_incidents_anterieurs": 0,
            "max_jours_retard_historique": np.nan,
            "montant_max_rembourse": np.nan,
            "numero_cycle": 1,
            "ratio_montant_historique": np.nan,
        }

    identifiants = set(precedents["credit_id"])
    echeances_precedentes = echeances[echeances["credit_id"].isin(identifiants)].copy()
    if niveau_individuel_seulement and "niveau_enregistrement" in echeances_precedentes.columns:
        echeances_precedentes = echeances_precedentes[
            echeances_precedentes["niveau_enregistrement"] == "individuel"
        ]
    echeances_precedentes["date_paiement_reelle"] = pd.to_datetime(
        echeances_precedentes["date_paiement_reelle"]
    )
    observees = echeances_precedentes[
        echeances_precedentes["date_paiement_reelle"].notna()
        & (echeances_precedentes["date_paiement_reelle"] <= reference)
    ]
    retards_par_credit = observees.groupby("credit_id")["jours_retard"].max()
    incidents = int((retards_par_credit >= 30).sum())
    maximum_retard = float(retards_par_credit.max()) if not retards_par_credit.empty else np.nan

    montant_max = np.nan
    correctement_rembourses: list[float] = []
    for precedent in precedents.itertuples(index=False):
        lignes = echeances_precedentes[echeances_precedentes["credit_id"] == precedent.credit_id]
        if lignes.empty:
            continue
        paiements = pd.to_datetime(lignes["date_paiement_reelle"])
        complet = paiements.notna().all() and bool((paiements <= reference).all())
        sans_incident = float(lignes["jours_retard"].max()) < 30
        if complet and sans_incident:
            correctement_rembourses.append(_nombre(precedent.montant_octroye, "montant_octroye"))
    if correctement_rembourses:
        montant_max = max(correctement_rembourses)

    montant_demande = float(credit["montant_octroye"])
    ratio_historique = montant_demande / montant_max if not np.isnan(montant_max) else np.nan
    return {
        "nb_credits_anterieurs": len(precedents),
        "nb_incidents_anterieurs": incidents,
        "max_jours_retard_historique": maximum_retard,
        "montant_max_rembourse": montant_max,
        "numero_cycle": int(len(precedents) + 1),
        "ratio_montant_historique": ratio_historique,
    }


def _credits_de_groupe(credits: pd.DataFrame, garanties: pd.DataFrame) -> set[str]:
    """Crédits dont l'emprunteur officiel est le GIE : `gie_id` renseigné et garantie
    `caution_solidaire_gie` — cf. `précision.txt` réponses 1 à 3, jamais inféré du seul
    segment (`femme_gie` n'implique pas toujours un GIE actif, cf. exploration J2)."""
    cautionnes = set(
        garanties.loc[garanties["type_garantie"] == "caution_solidaire_gie", "credit_id"]
    )
    avec_gie = set(credits.loc[credits["gie_id"].notna(), "credit_id"])
    return cautionnes & avec_gie


def _preparer_donnees_groupe(
    credits: pd.DataFrame, echeances: pd.DataFrame, tables_groupe: TablesGroupe
) -> tuple[
    set[str],
    dict[str, date],
    dict[str, list[AppartenanceGie]],
    dict[str, list[CreditGroupeAnterieur]],
    dict[str, list[EcheanceGroupe]],
    dict[str, list[CautionGroupe]],
]:
    """Pré-calcule, par `gie_id`, toutes les listes consommées par `calculer_features_groupe`.

    Le filtrage temporel (antérieur à la référence du crédit évalué) reste entièrement à la
    charge de cette dernière : on fournit ici l'historique complet du groupe, jamais coupé.
    """
    credits_groupe_ids = _credits_de_groupe(credits, tables_groupe.garanties)
    gie_par_credit: dict[str, str] = {
        str(ligne["credit_id"]): str(ligne["gie_id"])
        for ligne in credits.to_dict("records")
        if ligne["credit_id"] in credits_groupe_ids
    }

    date_creation_par_gie: dict[str, date] = {
        str(ligne["gie_id"]): pd.Timestamp(ligne["date_creation"]).date()
        for ligne in tables_groupe.groupes_gie.to_dict("records")
    }

    appartenances_par_gie: dict[str, list[AppartenanceGie]] = {}
    for ligne in tables_groupe.appartenances.to_dict("records"):
        sortie = (
            None if pd.isna(ligne["date_sortie"]) else pd.Timestamp(ligne["date_sortie"]).date()
        )
        appartenances_par_gie.setdefault(str(ligne["gie_id"]), []).append(
            AppartenanceGie(
                societaire_id=str(ligne["societaire_id"]),
                date_entree=pd.Timestamp(ligne["date_entree"]).date(),
                date_sortie=sortie,
            )
        )

    credits_groupe_par_gie: dict[str, list[CreditGroupeAnterieur]] = {}
    for ligne in credits.to_dict("records"):
        credit_id = str(ligne["credit_id"])
        if credit_id not in credits_groupe_ids:
            continue
        date_issue = (
            None if pd.isna(ligne["date_issue"]) else pd.Timestamp(ligne["date_issue"]).date()
        )
        credits_groupe_par_gie.setdefault(gie_par_credit[credit_id], []).append(
            CreditGroupeAnterieur(
                credit_id=credit_id,
                date_deblocage=pd.Timestamp(ligne["date_deblocage"]).date(),
                date_issue=date_issue,
                statut=str(ligne["statut"]),
            )
        )

    echeances_groupe_par_gie: dict[str, list[EcheanceGroupe]] = {}
    echeances_groupe = echeances[
        (echeances["niveau_enregistrement"] == "groupe")
        & echeances["credit_id"].isin(credits_groupe_ids)
    ]
    for ligne in echeances_groupe.to_dict("records"):
        gie_id = gie_par_credit.get(str(ligne["credit_id"]))
        if gie_id is None:
            continue
        paiement = (
            None
            if pd.isna(ligne["date_paiement_reelle"])
            else pd.Timestamp(ligne["date_paiement_reelle"]).date()
        )
        retard = None if pd.isna(ligne["jours_retard"]) else float(ligne["jours_retard"])
        echeances_groupe_par_gie.setdefault(gie_id, []).append(
            EcheanceGroupe(
                credit_id=str(ligne["credit_id"]), date_paiement_reelle=paiement, jours_retard=retard
            )
        )

    cautions_par_gie: dict[str, list[CautionGroupe]] = {}
    cautions_groupe = tables_groupe.garanties[
        (tables_groupe.garanties["type_garantie"] == "caution_solidaire_gie")
        & tables_groupe.garanties["credit_id"].isin(credits_groupe_ids)
    ]
    for ligne in cautions_groupe.to_dict("records"):
        gie_id = gie_par_credit.get(str(ligne["credit_id"]))
        if gie_id is None:
            continue
        cautions_par_gie.setdefault(gie_id, []).append(
            CautionGroupe(
                credit_id=str(ligne["credit_id"]),
                garantie_appelee=bool(ligne["garantie_appelee"]),
            )
        )

    return (
        credits_groupe_ids,
        date_creation_par_gie,
        appartenances_par_gie,
        credits_groupe_par_gie,
        echeances_groupe_par_gie,
        cautions_par_gie,
    )


_FEATURES_GROUPE_MANQUANTES: dict[str, float] = {
    "taille_groupe": np.nan,
    "anciennete_groupe_mois": np.nan,
    "nb_credits_groupe_anterieurs": np.nan,
    "nb_incidents_groupe_anterieurs": np.nan,
    "max_jours_retard_groupe_6m": np.nan,
    "nb_cautions_appelees_anterieures": np.nan,
}


def _construire_jeu(
    tables: TablesBrutes,
    date_fin: pd.Timestamp,
    *,
    niveau_individuel_seulement: bool,
    tables_groupe: TablesGroupe | None,
    catalogue_attendu: list[str],
) -> pd.DataFrame:
    """Construit une ligne par crédit sans utiliser le statut ni le défaut du crédit courant."""
    credits = tables.credits.copy()
    credits["date_deblocage"] = pd.to_datetime(credits["date_deblocage"])
    societaires = tables.societaires.copy().set_index("societaire_id")
    societaires["date_adhesion"] = pd.to_datetime(societaires["date_adhesion"])
    echeances = tables.echeances.copy()
    echeances["date_paiement_reelle"] = pd.to_datetime(echeances["date_paiement_reelle"])
    soldes = tables.soldes_mensuels.copy()
    soldes["mois"] = pd.to_datetime(soldes["mois"])
    taux_produits = tables.produits.set_index("produit_id")["taux_annuel"].astype(float).to_dict()
    cibles = construire_cible(credits, echeances, date_fin).set_index("credit_id")

    credits_groupe_ids: set[str] = set()
    donnees_groupe: tuple[
        dict[str, date],
        dict[str, list[AppartenanceGie]],
        dict[str, list[CreditGroupeAnterieur]],
        dict[str, list[EcheanceGroupe]],
        dict[str, list[CautionGroupe]],
    ] | None = None
    if tables_groupe is not None:
        (
            credits_groupe_ids,
            date_creation_par_gie,
            appartenances_par_gie,
            credits_groupe_par_gie,
            echeances_groupe_par_gie,
            cautions_par_gie,
        ) = _preparer_donnees_groupe(credits, echeances, tables_groupe)
        donnees_groupe = (
            date_creation_par_gie,
            appartenances_par_gie,
            credits_groupe_par_gie,
            echeances_groupe_par_gie,
            cautions_par_gie,
        )

    credits_par_societaire = {
        identifiant: groupe.sort_values(["date_deblocage", "credit_id"])
        for identifiant, groupe in credits.groupby("societaire_id", sort=False)
    }
    soldes_par_societaire = {
        identifiant: groupe.sort_values("mois")
        for identifiant, groupe in soldes.groupby("societaire_id", sort=False)
    }

    lignes: list[dict[str, object]] = []
    for credit in credits.sort_values(["date_deblocage", "credit_id"]).to_dict("records"):
        societaire_id = str(credit["societaire_id"])
        membre = societaires.loc[societaire_id]
        if isinstance(membre, pd.DataFrame):
            raise TypeError(f"Sociétaire dupliqué dans les données brutes : {societaire_id}")
        reference = pd.Timestamp(credit["date_deblocage"])
        revenu = _nombre_optionnel(membre["revenu_declare"], "revenu_declare")
        revenu_valide = revenu if revenu is not None and revenu > 0 else np.nan
        taux = taux_produits.get(str(credit["produit_id"]))
        if taux is None:
            raise ValueError(f"Produit absent du catalogue : {credit['produit_id']}")
        mensualite = mensualite_actuarielle(
            float(credit["montant_octroye"]), int(credit["duree_mois"]), taux
        )
        epargne = _features_epargne(soldes_par_societaire.get(societaire_id, pd.DataFrame()), reference)
        historique = _historique_observable(
            pd.Series(credit),
            credits_par_societaire[societaire_id],
            echeances,
            niveau_individuel_seulement=niveau_individuel_seulement,
        )
        moyenne_epargne = float(epargne["solde_epargne_moyen_6m"])
        montant = float(credit["montant_octroye"])
        cible = cibles.loc[str(credit["credit_id"])]

        groupe: dict[str, object]
        if donnees_groupe is not None and str(credit["credit_id"]) in credits_groupe_ids:
            gie_id = str(credit["gie_id"])
            (
                date_creation_par_gie,
                appartenances_par_gie,
                credits_groupe_par_gie,
                echeances_groupe_par_gie,
                cautions_par_gie,
            ) = donnees_groupe
            features_groupe = calculer_features_groupe(
                date_reference=reference.date(),
                date_creation_groupe=date_creation_par_gie[gie_id],
                appartenances=appartenances_par_gie.get(gie_id, []),
                credits_anterieurs=credits_groupe_par_gie.get(gie_id, []),
                echeances_groupe=echeances_groupe_par_gie.get(gie_id, []),
                cautions_anterieures=cautions_par_gie.get(gie_id, []),
            )
            groupe = {
                "taille_groupe": features_groupe.taille_groupe,
                "anciennete_groupe_mois": features_groupe.anciennete_groupe_mois,
                "nb_credits_groupe_anterieurs": features_groupe.nb_credits_groupe_anterieurs,
                "nb_incidents_groupe_anterieurs": features_groupe.nb_incidents_groupe_anterieurs,
                "max_jours_retard_groupe_6m": features_groupe.max_jours_retard_groupe_6m,
                "nb_cautions_appelees_anterieures": features_groupe.nb_cautions_appelees_anterieures,
            }
        elif donnees_groupe is not None:
            groupe = dict(_FEATURES_GROUPE_MANQUANTES)
        else:
            groupe = {}

        ligne: dict[str, object] = {
            "credit_id": credit["credit_id"],
            "societaire_id": societaire_id,
            "date_reference": reference,
            "classe_cible": cible["classe_cible"],
            "cible": cible["cible"],
            # Colonnes d'audit : jamais présentes dans `codes_features_socle()` ni dans X.
            "sexe_audit": str(membre["sexe"]),
            "segment_audit": str(membre["segment"]),
            "tranche_montant_audit": _tranche_montant(
                _nombre(credit["montant_octroye"], "montant_octroye")
            ),
            "anciennete_societaire_mois": mois_ecoules(
                pd.Timestamp(membre["date_adhesion"]), reference
            ),
            "nb_personnes_a_charge": int(
                _nombre(membre["nb_personnes_a_charge"], "nb_personnes_a_charge")
            ),
            "zone_residence": str(membre["zone"]),
            "parts_sociales_montant": int(_nombre(membre["parts_sociales"], "parts_sociales")),
            "revenu_mensuel_declare": revenu_valide,
            "ratio_endettement": mensualite / revenu_valide if not np.isnan(revenu_valide) else np.nan,
            "duree_demandee_mois": int(credit["duree_mois"]),
            **epargne,
            "ratio_epargne_revenu": (
                min(moyenne_epargne / revenu_valide, 5.0)
                if not np.isnan(revenu_valide)
                else np.nan
            ),
            "anciennete_epargne_mois": mois_ecoules(
                pd.Timestamp(membre["date_adhesion"]), reference
            ),
            "ratio_epargne_montant": min(moyenne_epargne / montant, 3.0) if montant > 0 else np.nan,
            **historique,
            **groupe,
        }
        lignes.append(ligne)

    resultat = pd.DataFrame(lignes)
    # La cible doit conserver ses absences (indéterminé / non mûr), distinctes de 0.
    resultat["cible"] = resultat["cible"].astype("Int64")
    resultat["split"] = attribuer_split(resultat["date_reference"])
    resultat["tendance_epargne_12m"] = pd.Categorical(
        resultat["tendance_epargne_12m"], categories=ORDRE_TENDANCE, ordered=True
    )
    attendu = {"credit_id", "societaire_id", "date_reference", "classe_cible", "cible", "split"}
    absent = set(catalogue_attendu).difference(resultat.columns)
    if absent or not attendu.issubset(resultat.columns):
        raise AssertionError(f"Jeu de features incomplet : {sorted(absent)}")
    return resultat


def construire_jeu_socle(tables: TablesBrutes, date_fin: pd.Timestamp) -> pd.DataFrame:
    """Construit le jeu SOCLE : comportement inchangé depuis J1, aucune variable de groupe."""
    return _construire_jeu(
        tables,
        date_fin,
        niveau_individuel_seulement=False,
        tables_groupe=None,
        catalogue_attendu=codes_features_socle(),
    )


def construire_jeu_enrichi(
    tables: TablesBrutes, tables_groupe: TablesGroupe, date_fin: pd.Timestamp
) -> pd.DataFrame:
    """Construit le jeu enrichi : ajoute la couche solidaire, filtre l'historique individuel
    aux seules échéances de niveau individuel (5.10)."""
    return _construire_jeu(
        tables,
        date_fin,
        niveau_individuel_seulement=True,
        tables_groupe=tables_groupe,
        catalogue_attendu=codes_features_enrichi(),
    )


def ecrire_jeu_socle(source: Path, sortie: Path, date_fin: pd.Timestamp) -> pd.DataFrame:
    dataset = construire_jeu_socle(lire_tables_brutes(source), date_fin)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_parquet(sortie, index=False)
    return dataset


def ecrire_jeu_enrichi(source: Path, sortie: Path, date_fin: pd.Timestamp) -> pd.DataFrame:
    dataset = construire_jeu_enrichi(
        lire_tables_brutes(source), lire_tables_groupe(source), date_fin
    )
    sortie.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_parquet(sortie, index=False)
    return dataset
