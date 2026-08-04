"""
SOLIDA -- Couche FEATURE ENGINEERING (separee du generateur).
Prend les tables BRUTES du SIG et derive les variables du modele, en trois blocs :
  - SOCLE (universel, 100% du portefeuille) : epargne + historique remboursement + profil.
  - SOLIDAIRE (conditionnel, segment GIE) : remboursement du groupe, taille, deja secouru.
  - SECTORIEL : degradation recente du secteur.
Toutes les variables derivees sont LEAK-FREE (calculees a la date de deblocage).
"""
import numpy as np, pandas as pd
from pathlib import Path

def construire(out=None):
    out = Path(out) if out else Path(__file__).resolve().parent.parent / "sorties"
    cr = pd.read_parquet(out / "credits.parquet")
    soc = pd.read_parquet(out / "societaires.parquet")
    cpt = pd.read_parquet(out / "comptes_epargne.parquet").drop(columns=["compte_id"])
    gar = pd.read_parquet(out / "garanties.parquet"); gar["date_engagement"] = pd.to_datetime(gar["date_engagement"])

    cr = cr[cr["defaut"] >= 0].copy()
    cr["date_deblocage"] = pd.to_datetime(cr["date_deblocage"]); cr["date_issue"] = pd.to_datetime(cr["date_issue"])
    cr = cr.sort_values("date_deblocage").reset_index(drop=True)

    attrs = soc.set_index("societaire_id")[["anciennete_societaire_mois","age","nb_personnes_a_charge",
        "parts_sociales","revenu_declare","niveau_education","taille_gie"]]
    J = cr.join(attrs, on="societaire_id").join(cpt.set_index("societaire_id"), on="societaire_id")
    edu = {"aucun":0,"primaire":1,"secondaire":2,"superieur":3, None:np.nan}
    J["edu"] = J["niveau_education"].map(edu)
    # flags de segment (le segment est une donnee du SIG : produit souscrit)
    for s in ["salarie","jeune","agricole","femme_gie"]:
        J[f"seg_{s}"] = (J["segment"] == s).astype(int)
    # ratio garantie epargne nantie / credit
    solde = cpt.set_index("societaire_id")["solde_epargne_moyen_6m"]
    J["ratio_garantie"] = (J["societaire_id"].map(solde) / J["montant_octroye"]).clip(0, 3)

    # --- TRAJECTOIRE D'EPARGNE DYNAMIQUE (signal central du modele mutualiste) ---
    # 1) effort d'epargne : solde rapporte au revenu declare
    J["ratio_epargne_revenu"] = (J["solde_epargne_moyen_6m"] / J["revenu_declare"]).clip(0, 5)
    # 2) anciennete de la RELATION d'epargne au moment de la demande (mois epargnes avant credit)
    adh = soc.set_index("societaire_id")["date_adhesion"]
    J["anciennete_epargne_mois"] = ((J["date_deblocage"] - pd.to_datetime(J["societaire_id"].map(adh)))
                                     .dt.days / 30.44).clip(lower=0).round(1)
    # 3) tendance qualitative : epargne en hausse / stable / baisse (lisible dans la fiche)
    J["tendance_epargne"] = np.select(
        [J["croissance_epargne_12m"] > 0.10, J["croissance_epargne_12m"] < -0.05],
        [1, -1], default=0)
    # 4) regularite normalisee (part des mois avec depot)
    J["regularite_epargne"] = J["nb_mois_avec_depot_12m"] / 12.0

    # --- historique de remboursement (leak-free) ---
    hist = {}
    for r in cr.itertuples():
        hist.setdefault(r.societaire_id, []).append((r.date_issue, r.defaut, r.jours_retard_max))
    for k in hist: hist[k].sort()
    nba, inca, jrmax, jrmoy = [], [], [], []
    for r in cr.itertuples():
        passe = [(d, jr) for (t, d, jr) in hist[r.societaire_id] if t < r.date_deblocage]
        nba.append(len(passe)); inca.append(int(sum(d for d, _ in passe)))
        jrs = [jr for _, jr in passe if pd.notna(jr)]
        jrmax.append(max(jrs) if jrs else 0.0); jrmoy.append(float(np.mean(jrs)) if jrs else 0.0)
    J["nb_credits_ant"] = nba; J["nb_incidents_ant"] = inca
    J["jours_retard_max_ant"] = jrmax; J["jours_retard_moyen_ant"] = jrmoy

    # --- SOLIDAIRE (GIE) : remboursement du groupe hors soi, leak-free ---
    gi = {}
    for r in cr.itertuples():
        if pd.notna(r.gie_id): gi.setdefault(r.gie_id, []).append((r.date_issue, r.defaut, r.societaire_id))
    for g in gi: gi[g].sort()
    grp, en_gie = [], []
    for r in cr.itertuples():
        if pd.isna(r.gie_id): grp.append(np.nan); en_gie.append(0); continue
        en_gie.append(1)
        obs = [d for (t, d, s) in gi[r.gie_id] if t < r.date_deblocage and s != r.societaire_id]
        grp.append(1 - np.mean(obs) if obs else np.nan)
    J["grp_taux_remb"] = grp; J["en_gie"] = en_gie
    # deja secouru : caution appelee anterieure au benefice du membre
    app = gar[gar["garantie_appelee"]]
    sec = {}
    for r in app.itertuples(): sec.setdefault(r.beneficiaire_societaire_id, []).append(r.date_engagement)
    J["deja_secouru"] = [sum(1 for de in sec.get(r.societaire_id, []) if de < r.date_deblocage) for r in cr.itertuples()]

    # --- SECTORIEL : taux de souffrance recent du secteur (agricole surtout) leak-free ---
    seg_hist = {}
    for r in cr.itertuples(): seg_hist.setdefault(r.segment, []).append((r.date_issue, r.defaut))
    for s in seg_hist: seg_hist[s].sort()
    rec = []
    for r in cr.itertuples():
        fen = pd.Timestamp(r.date_deblocage) - pd.DateOffset(months=12)
        obs = [d for (t, d) in seg_hist[r.segment] if fen <= t < r.date_deblocage]
        rec.append(np.mean(obs) if obs else np.nan)
    J["seg_souffrance_recent"] = rec

    socle = ["nb_mois_avec_depot_12m","regularite_epargne","solde_epargne_moyen_6m",
        "croissance_epargne_12m","tendance_epargne","volatilite_epargne",
        "ratio_epargne_revenu","anciennete_epargne_mois",
        "ratio_garantie","anciennete_societaire_mois","endettement","numero_cycle","est_primo",
        "montant_octroye","nb_personnes_a_charge","parts_sociales","revenu_declare","edu","age",
        "nb_credits_ant","nb_incidents_ant","jours_retard_max_ant","jours_retard_moyen_ant",
        "seg_salarie","seg_jeune","seg_agricole"]
    solidaire = socle + ["en_gie","taille_gie","grp_taux_remb","deja_secouru"]
    sectoriel = solidaire + ["seg_souffrance_recent"]
    y = J["defaut"].astype(int).values
    return J, y, {"socle": socle, "+solidaire": solidaire, "+sectoriel": sectoriel}

if __name__ == "__main__":
    J, y, sets = construire()
    print(f"credits resolus: {len(J)} | taux souffrance: {y.mean():.3f}")
    print(f"couverture grp_taux_remb: {J['grp_taux_remb'].notna().mean():.2%} "
          f"| part en GIE: {J['en_gie'].mean():.2%}")
