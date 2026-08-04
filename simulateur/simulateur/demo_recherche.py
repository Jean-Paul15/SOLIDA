"""Demo agent COOPEC : recherche par nom/numero -> dossier 360 (profil, epargne, credits, GIE)."""
import sys, pandas as pd
from pathlib import Path
out = Path(__file__).resolve().parent.parent / "sorties"
soc = pd.read_parquet(out / "societaires.parquet"); cr = pd.read_parquet(out / "credits.parquet")
cpt = pd.read_parquet(out / "comptes_epargne.parquet"); gar = pd.read_parquet(out / "garanties.parquet")

q = sys.argv[1] if len(sys.argv) > 1 else "MENSAH"
m = soc[soc["nom_complet"].str.contains(q, case=False, na=False) | soc["numero_membre"].astype(str).eq(q)]
if m.empty: print(f"Aucun membre pour '{q}'."); sys.exit()
r = m.iloc[0]; e = cpt[cpt["societaire_id"] == r["societaire_id"]]
print("="*60); print(f"  {r['nom_complet']}  (membre {r['numero_membre']})"); print("="*60)
print(f"  Caisse {r['caisse_id']} | segment {r['segment']} | zone {r['zone']}")
print(f"  Adhesion/epargne depuis : {pd.Timestamp(r['date_adhesion']).date()} ({r['anciennete_societaire_mois']} mois)")
if len(e):
    ee = e.iloc[0]
    print(f"  Epargne : solde moyen {ee['solde_epargne_moyen_6m']:.0f} FCFA | "
          f"{ee['nb_mois_avec_depot_12m']}/12 mois avec depot | croissance {ee['croissance_epargne_12m']:+.2f}")
if pd.notna(r["gie_id"]): print(f"  GIE (caution solidaire) : {r['gie_id']} (taille {int(r['taille_gie'])})")
h = cr[cr["societaire_id"] == r["societaire_id"]].sort_values("date_deblocage")
print(f"\n  Historique de credit ({len(h)}) :")
for c in h.itertuples():
    et = {1:"EN SOUFFRANCE", 0:"solde", -1:"en cours"}[c.defaut]
    jr = "" if pd.isna(c.jours_retard_max) else f" | retard max {int(c.jours_retard_max)}j"
    print(f"    cycle {c.numero_cycle} | {pd.Timestamp(c.date_deblocage).date()} | {c.montant_octroye:>8d} FCFA | {c.duree_mois}m | {c.statut}{jr}")
g = gar[gar["beneficiaire_societaire_id"] == r["societaire_id"]]
if len(g):
    print(f"\n  Garanties : " + ", ".join(f"{t}×{n}" for t,n in g['type_garantie'].value_counts().items()) +
          f" (cautions appelees : {int(g['garantie_appelee'].sum())})")
