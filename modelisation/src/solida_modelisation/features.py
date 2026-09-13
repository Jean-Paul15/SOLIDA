"""Features SOCLE calculées sans regarder le futur du crédit évalué."""

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .catalogue import ORDRE_TENDANCE, codes_features_socle
from .cible import construire_cible
from .finance import mensualite_actuarielle
from .splits import attribuer_split


@dataclass(frozen=True)
class TablesBrutes:
    societaires: pd.DataFrame
    credits: pd.DataFrame
    echeances: pd.DataFrame
    soldes_mensuels: pd.DataFrame
    produits: pd.DataFrame


def lire_tables_brutes(dossier: Path) -> TablesBrutes:
    """Lit les seules tables nécessaires au SOCLE depuis une sortie du simulateur."""
    return TablesBrutes(
        societaires=pd.read_parquet(dossier / "societaires.parquet"),
        credits=pd.read_parquet(dossier / "credits.parquet"),
        echeances=pd.read_parquet(dossier / "echeances.parquet"),
        soldes_mensuels=pd.read_parquet(dossier / "solde_mensuel_epargne.parquet"),
        produits=pd.read_parquet(dossier / "produits_credit.parquet"),
    )


def mois_ecoules(debut: pd.Timestamp, fin: pd.Timestamp) -> int:
    """Nombre de mois révolus entre deux dates, borné à zéro."""
    valeur = (fin.year - debut.year) * 12 + fin.month - debut.month
    if fin.day < debut.day:
        valeur -= 1
    return max(valeur, 0)


def _tendance(croissance: float) -> str:
    if croissance > 0.10:
        return "hausse"
    if croissance < -0.05:
        return "erosion"
    return "stable"


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
    """Utilise seulement des mois totalement clos avant la date de référence."""
    debut_mois_reference = date_reference.to_period("M").to_timestamp()
    historiques = soldes[pd.to_datetime(soldes["mois"]) < debut_mois_reference].sort_values("mois")
    derniers_6 = historiques.tail(6)
    derniers_12 = historiques.tail(12)
    valeurs_6 = derniers_6["solde_fin_mois"].astype(float).to_numpy()
    valeurs_12 = derniers_12["solde_fin_mois"].astype(float).to_numpy()
    moyenne_6 = float(valeurs_6.mean()) if len(valeurs_6) else 0.0
    depots = int((derniers_12["total_depots"] > 0).sum())
    point_depart = float(valeurs_12[0]) if len(valeurs_12) >= 12 else 0.0
    dernier_solde = float(valeurs_12[-1]) if len(valeurs_12) else 0.0
    croissance = (dernier_solde - point_depart) / max(abs(point_depart), 1_000.0)
    variations = np.diff(np.r_[0.0, valeurs_12]) if len(valeurs_12) else np.array([0.0])
    volatilite = float(np.std(variations) / max(float(valeurs_12.mean()), 1.0)) if len(valeurs_12) else 0.0
    return {
        "solde_epargne_moyen_6m": moyenne_6,
        "nb_mois_avec_depot_12m": depots,
        "tendance_epargne_12m": _tendance(croissance),
        "volatilite_epargne": volatilite,
    }


def _historique_observable(
    credit: pd.Series, credits_societaire: pd.DataFrame, echeances: pd.DataFrame
) -> dict[str, float | int]:
    """Construit l'historique avec les seuls paiements réellement connus à la date donnée."""
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


def construire_jeu_socle(tables: TablesBrutes, date_fin: pd.Timestamp) -> pd.DataFrame:
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
            pd.Series(credit), credits_par_societaire[societaire_id], echeances
        )
        moyenne_epargne = float(epargne["solde_epargne_moyen_6m"])
        montant = float(credit["montant_octroye"])
        cible = cibles.loc[str(credit["credit_id"])]
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
    absent = set(codes_features_socle()).difference(resultat.columns)
    if absent or not attendu.issubset(resultat.columns):
        raise AssertionError(f"Jeu SOCLE incomplet : {sorted(absent)}")
    return resultat


def ecrire_jeu_socle(source: Path, sortie: Path, date_fin: pd.Timestamp) -> pd.DataFrame:
    dataset = construire_jeu_socle(lire_tables_brutes(source), date_fin)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_parquet(sortie, index=False)
    return dataset
