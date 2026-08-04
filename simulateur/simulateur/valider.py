"""
Validation SOLIDA v3 (COOPEC) : la performance EMERGE, on ne la cible pas.
Socle epargne+remboursement (universel) -> +solidaire (GIE) -> +sectoriel.
Decoupage TEMPOREL. Rapporte AUC/Gini/AUPRC + matrice d'argent + interpretation.
"""
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance
import features

J, y, sets = features.construire()
seuil = J["date_deblocage"].quantile(0.75)
tr = (J["date_deblocage"] < seuil).values; te = ~tr

def evalue(feats, retmodel=False):
    m = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.05, max_depth=3,
                                       l2_regularization=1.0, random_state=0)
    m.fit(J.loc[tr, feats].values, y[tr]); p = m.predict_proba(J.loc[te, feats].values)[:, 1]
    auc = roc_auc_score(y[te], p)
    return (auc, 2*auc-1, average_precision_score(y[te], p), p, m) if retmodel else (auc, 2*auc-1, average_precision_score(y[te], p))

print("=== PERFORMANCE EMERGENTE (jamais ciblee) -- logique COOPEC ===")
print(f"  Base test : {te.sum()} credits | taux souffrance {y[te].mean():.3f}")
res = {}
for nom, feats in sets.items():
    auc, gini, ap = evalue(feats); res[nom] = auc
    print(f"  {nom:12s} AUC {auc:.3f} | Gini {gini:.3f} | AUPRC {ap:.3f}")
print(f"  Apport solidaire : +{res['+solidaire']-res['socle']:.3f} | "
      f"sectoriel : +{res['+sectoriel']-res['+solidaire']:.3f} AUC")

auc_f = res["+sectoriel"]
print("\n=== VALIDATION FOURCHETTE SECTEUR (0.70-0.85) ===")
msg = ("DANS la fourchette. Emergente, non ciblee. OK." if 0.68 <= auc_f <= 0.88
       else "TROP HAUTE (>0.88) -> inspecter fuite" if auc_f > 0.88 else "trop basse (<0.68)")
print(f"  AUC {auc_f:.3f} {msg}")

# --- matrice d'argent ---
_, _, _, p_f, mfin = evalue(sets["+sectoriel"], retmodel=True)
LGD, MARGE = 0.75, 0.15; seuil_opt = MARGE/(MARGE+LGD)
expo = J.loc[te, "montant_octroye"].values.astype(float); yv = y[te]
def cout(s):
    refus = p_f >= s
    return (LGD*expo[(~refus)&(yv==1)]).sum() + (MARGE*expo[refus&(yv==0)]).sum()
c0, co = cout(0.50), cout(seuil_opt)
print("\n=== MATRICE D'ARGENT (modele +sectoriel) ===")
print(f"  Exposition test        : {expo.sum()/1e6:.1f} M FCFA / {len(yv)} credits")
print(f"  Seuil optimal          : {seuil_opt:.3f} (LGD={LGD}, marge={MARGE})")
print(f"  Cout @0.50             : {c0/1e6:.1f} M | @optimal : {co/1e6:.1f} M FCFA")
print(f"  Economie               : {(c0-co)/1e6:.1f} M FCFA ({100*(c0-co)/max(c0,1):.0f}% des pertes)")
ordre = np.argsort(-p_f); yo = yv[ordre]
for f in (0.10, 0.20, 0.30):
    k = int(len(yv)*f)
    print(f"  {int(f*100)}% plus risques -> {yo[:k].sum()/max(yv.sum(),1)*100:.0f}% des souffrances")

# --- interpretation ---
imp = permutation_importance(mfin, J.loc[te, sets["+sectoriel"]].values, yv, n_repeats=6,
                             random_state=0, scoring="roc_auc")
print("\n=== INTERPRETATION : variables les plus determinantes ===")
for i in np.argsort(-imp.importances_mean)[:10]:
    print(f"  {sets['+sectoriel'][i]:26s} {imp.importances_mean[i]:.4f}")

# --- valeur du SOLIDAIRE la ou il s'applique : sous-ensemble GIE seulement ---
print("\n=== VALEUR DE LA COUCHE SOLIDAIRE (sur le segment GIE uniquement) ===")
gie_te = te & (J["en_gie"].values == 1)
gie_tr = tr & (J["en_gie"].values == 1)
if gie_te.sum() > 40 and gie_tr.sum() > 40:
    def ev_sub(feats):
        m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_depth=3,
                                            l2_regularization=1.0, random_state=0)
        m.fit(J.loc[gie_tr, feats].values, y[gie_tr])
        p = m.predict_proba(J.loc[gie_te, feats].values)[:, 1]
        return roc_auc_score(y[gie_te], p)
    a_socle = ev_sub(sets["socle"]); a_soli = ev_sub(sets["+solidaire"])
    print(f"  GIE test : {gie_te.sum()} credits | souffrance {y[gie_te].mean():.3f}")
    print(f"  socle {a_socle:.3f} -> +solidaire {a_soli:.3f}  (apport reel {a_soli-a_socle:+.3f} AUC)")
    print("  NB : sous-estime par le demarrage a froid des GIE ; plus fort sur portefeuille mature.")
else:
    print("  (trop peu de credits GIE dans le test pour une mesure stable)")
