"""
SOLIDA -- Moteur de DECISION (couche au-dessus du score).

Trois briques, toutes transparentes et parametrables par la cooperative :
  1. GRILLE DE DECISION parametrable : seuils issus de la matrice de couts
     (seuil economique = marge / (marge + LGD)), modifiables par caisse/pays.
  2. CREDIT PROGRESSIF : plafond conseille fonde sur l'historique rembourse et
     le risque -- avec la TRAJECTOIRE de progression si le membre tient ses
     engagements (incitation dynamique, mecanisme fondateur de la microfinance).
  3. FICHE DE JUSTIFICATION ACTIONNABLE : pourquoi cette decision, ET
     ce que le societaire peut faire pour ameliorer son dossier (conditions de
     reexamen explicites, verifiables dans le systeme).

Aucune boite noire : chaque regle est lisible, auditable, modifiable.
"""
import numpy as np, pandas as pd

# --- 1. Grille parametrable (valeurs par defaut, surchargeables par caisse) ---
POLITIQUE_DEFAUT = {
    "lgd": 0.75,               # perte en cas de defaut
    "marge": 0.15,             # marge nette sur un credit sain
    "coef_progression": 1.5,   # plafond = 1.5x le plus gros credit rembourse
    "plafond_produit": 3000000,
    "montant_plancher": 50000,
    "regularite_cible": 0.75,  # 9 mois / 12 avec depot
    "mois_observation": 3,     # duree de la periode de reexamen
}

def seuils(pol=POLITIQUE_DEFAUT):
    """Seuil economique + zone de vigilance (decision partagee avec l'agent)."""
    s_eco = pol["marge"] / (pol["marge"] + pol["lgd"])
    return {"accord": s_eco * 0.6, "vigilance": s_eco, "refus": s_eco * 1.6}

def decider(pd_risque, pol=POLITIQUE_DEFAUT):
    s = seuils(pol)
    if pd_risque < s["accord"]:    return "ACCORD"
    if pd_risque < s["vigilance"]: return "ACCORD SOUS CONDITIONS"
    if pd_risque < s["refus"]:     return "EXAMEN RENFORCE"
    return "DEFAVORABLE"

# --- 2. Credit progressif : plafond conseille + trajectoire ---
def plafond_conseille(montant_demande, max_rembourse, pd_risque, pol=POLITIQUE_DEFAUT):
    """Plafond = capacite historique x facteur de progression, module par le risque."""
    base = max(max_rembourse * pol["coef_progression"], pol["montant_plancher"])
    modulation = float(np.clip(1.3 - 2.0 * pd_risque, 0.4, 1.2))
    plaf = int(min(base * modulation, pol["plafond_produit"], montant_demande))
    return max(plaf, pol["montant_plancher"])

def trajectoire_progression(plafond_actuel, n_cycles=3, pol=POLITIQUE_DEFAUT):
    """Ce que le membre peut obtenir s'il rembourse sans incident (incitation dynamique)."""
    traj, p = [], plafond_actuel
    for c in range(1, n_cycles + 1):
        p = int(min(p * pol["coef_progression"], pol["plafond_produit"]))
        traj.append((c, p))
    return traj

# --- 3. Fiche de justification ACTIONNABLE ---
def conditions_reexamen(dossier, pol=POLITIQUE_DEFAUT):
    """Leviers concrets, verifiables dans le SIG, que le societaire peut activer."""
    c = []
    reg = dossier.get("regularite_epargne", 0)
    if reg < pol["regularite_cible"]:
        manque = int(round((pol["regularite_cible"] - reg) * 12))
        c.append(f"Effectuer un depot chaque mois pendant {pol['mois_observation']} mois "
                 f"(regularite actuelle {reg*100:.0f}%, cible {pol['regularite_cible']*100:.0f}%, "
                 f"soit ~{manque} mois de depot a rattraper).")
    if dossier.get("ratio_garantie", 0) < 0.5:
        cible = int(dossier.get("montant_demande", 0) * 0.5)
        c.append(f"Porter l'epargne nantie a {cible:,} FCFA (50% du montant demande) "
                 f"pour renforcer la garantie.".replace(",", " "))
    if dossier.get("endettement", 0) > 0.5:
        c.append("Reduire le montant demande ou allonger la duree : la charge de "
                 "remboursement depasse 50% du revenu estime.")
    if dossier.get("tendance_epargne", 0) < 0:
        c.append("Stabiliser le solde d'epargne : la trajectoire est orientee a la baisse "
                 "sur les 12 derniers mois.")
    if dossier.get("deja_secouru", 0) > 0:
        c.append("Regulariser la situation vis-a-vis du groupe : une caution a deja ete "
                 "appelee pour ce membre.")
    if not c:
        c.append("Aucun levier bloquant : le dossier peut etre reexamine des le prochain cycle.")
    return c

def fiche(dossier, pd_risque, contributions, pol=POLITIQUE_DEFAUT):
    """Fiche complete remise a l'agent (et explicable au societaire)."""
    dec = decider(pd_risque, pol)
    plaf = plafond_conseille(dossier.get("montant_demande", 0),
                             dossier.get("max_rembourse", 0), pd_risque, pol)
    L = []
    L.append("="*64)
    L.append(f"  FICHE DE DECISION -- {dossier.get('nom','(membre)')} ({dossier.get('numero','')})")
    L.append("="*64)
    L.append(f"  Probabilite de defaut estimee : {pd_risque*100:.1f}%")
    L.append(f"  Decision recommandee          : {dec}")
    L.append(f"  Montant demande               : {dossier.get('montant_demande',0):,} FCFA".replace(",", " "))
    L.append(f"  Plafond conseille             : {plaf:,} FCFA".replace(",", " "))
    L.append("\n  Facteurs determinants :")
    for nom, pts in contributions:
        signe = "+" if pts >= 0 else "-"
        L.append(f"    {signe} {nom:38s} {abs(pts):>5.0f} points")
    L.append("\n  Conditions de reexamen (actionnables) :")
    for i, c in enumerate(conditions_reexamen(dossier, pol), 1):
        L.append(f"    {i}. {c}")
    L.append("\n  Trajectoire si remboursement sans incident :")
    for cyc, p in trajectoire_progression(plaf, 3, pol):
        L.append(f"    cycle +{cyc} : jusqu'a {p:,} FCFA".replace(",", " "))
    L.append("\n  Decision finale : l'agent de credit. SOLIDA documente et propose.")
    return "\n".join(L)

if __name__ == "__main__":
    s = seuils()
    print(f"Grille parametrable -> accord < {s['accord']:.3f} | vigilance < {s['vigilance']:.3f} "
          f"| examen renforce < {s['refus']:.3f}")
    dossier = {"nom":"AMEGAN Enyonam","numero":"100006","montant_demande":250000,
               "max_rembourse":120000,"regularite_epargne":0.42,"ratio_garantie":0.31,
               "endettement":0.58,"tendance_epargne":-1,"deja_secouru":0}
    contribs = [("Regularite d'epargne (5/12 mois)", -34), ("Anciennete de la relation (59 mois)", +21),
                ("Ratio d'endettement (58%)", -18), ("Historique de remboursement (0 incident)", +26),
                ("Epargne nantie (31% du montant)", -12)]
    print(fiche(dossier, 0.19, contribs))
