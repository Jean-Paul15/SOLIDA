"""
SOLIDA -- Generateur CORE-SIM v3 (logique COOPEC / CIF).

Modele reel des reseaux mutualistes (FUCEC, RCPB, PAMECAS, FECECAM, Kafo, Nyesigiso) :
- caisse d'EPARGNE d'abord : tout membre epargne ; l'epargne est la porte d'entree du credit.
- ~25% des membres empruntent (bilan social FUCEC : 70 646 emprunteurs / 287 643 societaires).
- credit INDIVIDUEL dominant, adosse a l'epargne (epargne nantie) ; la caution solidaire
  est un SEGMENT (GIE femmes), pas le coeur.
- defaut = creance en souffrance (PAR 90j), calibre ~9% (secteur Togo ~11%, norme 3%).

Le generateur produit uniquement des DONNEES BRUTES (ce qui est dans le SIG).
L'enrichissement (variables derivees, relationnelles) se fait dans features.py.
Performance EMERGENTE, jamais ciblee. Reproductible. Aucune date > date_fin (08/2026).
"""
import numpy as np, pandas as pd, yaml
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
def charger_config(p=RACINE / "config/config.yaml"): return yaml.safe_load(open(p))
def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))
def z(a):
    a = np.asarray(a, float); s = a.std(); return (a - a.mean()) / (s if s > 1e-9 else 1.0)

PATRONYMES = ["ADJOVI","AGBEKO","AGBODJAN","AKAKPO","AMEGAN","AMOUZOU","ATSU","AYITE","DOSSOU",
    "EKUE","FOLI","GAKPE","KODJO","KOUASSI","KPODAR","LAWSON","MENSAH","NYAVOR","SODJI","SOSSOU",
    "TCHALLA","TETTEH","ZANOU","ABALO","ALASSANI","BAKARI","DJAGBA","HODABALO","LARE","PIYABALO",
    "TCHASSANTI","WALLA","ESSOZIMNA","AMEVO","GNIMASSOU","KANLANFEI","BATABA","AKUE","DEGBEVI",
    "OURO","SAMBIANI","TCHAGNAO","BASSABI","AZIABLI","KOSSIVI","DABLA","AFANOU","GBIKPI"]
PRENOMS_M = ["Kokou","Kofi","Komla","Kwami","Yao","Kodjo","Kossi","Selom","Elom","Edem","Mawuli",
    "Senyo","Delali","Koffi","Komi","Folly","Essohanam","Amevo","Sena","Kossivi","Mensah","Ayao"]
PRENOMS_F = ["Akouvi","Ama","Afi","Adjo","Adjovi","Akossiwa","Abra","Essi","Adzo","Dede","Enyonam",
    "Ablavi","Afiwa","Akpene","Sitsope","Mawusi","Yawa","Dela","Akuvi","Elolo","Sedjro","Afia"]

def noms(rng, sexes):
    # Deux societaires distincts avec le meme nom complet ne sont pas un doublon technique
    # (societaire_id reste unique) mais brouillent la recherche par nom pour l'agent : on
    # garantit donc l'unicite du nom complet sur toute la population generee. L'espace de
    # combinaisons (patronymes x prenoms, avec ou sans second prenom) depasse largement
    # n_membres, une nouvelle tentative suffit presque toujours ; le second prenom force en
    # dernier recours elargit encore la combinatoire plutot que d'ajouter un suffixe visible
    # qui casserait le realisme des donnees.
    utilises = set()
    out = []
    for s in sexes:
        base = PRENOMS_F if s == "F" else PRENOMS_M
        for _ in range(500):
            pat = rng.choice(PATRONYMES)
            prenom = rng.choice(base)
            p2 = (" " + rng.choice(PRENOMS_M + PRENOMS_F)) if rng.random() < 0.4 else ""
            nom = f"{pat} {prenom}{p2}"
            if nom not in utilises:
                break
        else:
            nom = f"{pat} {prenom} {rng.choice(PRENOMS_M + PRENOMS_F)} {rng.choice(PRENOMS_M + PRENOMS_F)}"
        utilises.add(nom)
        out.append(nom)
    return out

# ------------------------------------------------------------------ membres (tous epargnants)
def gen_membres(cfg, rng):
    n = cfg["n_membres"]; fin = pd.Timestamp(cfg["date_fin"])
    jours_max = int(cfg["anciennete_max_annees"] * 365)
    anc_j = (rng.beta(1.6, 2.2, n) * jours_max).astype(int)
    adhesion = fin - pd.to_timedelta(anc_j, unit="D")   # = debut de l'epargne

    segs = list(cfg["segments"].keys())
    poids = np.array([cfg["segments"][s] for s in segs]); poids /= poids.sum()
    segment = rng.choice(segs, n, p=poids)
    # sexe : le segment femme_gie est feminin ; sinon mixte
    sexe = np.where(segment == "femme_gie", "F", rng.choice(["F","M"], n, p=[0.55,0.45]))
    zone = rng.choice(cfg["zones"], n, p=cfg["zones_poids"])
    # agricole surtout rural
    zone = np.where((segment == "agricole") & (rng.random(n) < 0.6), "rural", zone)

    fiabilite = rng.normal(0, 1, n)                          # fiabilite generale (cachee)
    discipline = 0.6 * fiabilite + 0.8 * rng.normal(0, 1, n) # discipline d'epargne
    edu_latent = 0.6 * fiabilite + rng.normal(0, 0.9, n)
    niveaux = np.array(["aucun","primaire","secondaire","superieur"])
    niveau_education = niveaux[np.clip(np.digitize(edu_latent, [-0.8, 0.1, 1.0]), 0, 3)]

    df = pd.DataFrame({
        "societaire_id": [f"SOC-{i:06d}" for i in range(n)],
        "numero_membre": [f"{100000+i:06d}" for i in range(n)],
        "nom_complet": noms(rng, sexe),
        "caisse_id": [f"CAI-{k:02d}" for k in rng.integers(0, cfg["n_caisses"], n)],
        "date_adhesion": adhesion,
        "anciennete_societaire_mois": (anc_j / 30).astype(int),
        "segment": segment, "age": rng.integers(20, 68, n), "sexe": sexe,
        "statut_matrimonial": rng.choice(["celibataire","marie","veuf","divorce"], n, p=[0.28,0.58,0.08,0.06]),
        "zone": zone, "nb_personnes_a_charge": rng.poisson(2.4, n),
        "niveau_education": niveau_education, "parts_sociales": rng.integers(5000, 60000, n),
        "revenu_declare": rng.lognormal(np.log(85000), 0.5, n).astype(int),
        "lat_fiabilite": fiabilite, "lat_discipline": discipline,
    })
    # jeune : age plus bas
    df.loc[df["segment"] == "jeune", "age"] = rng.integers(18, 30, (df["segment"]=="jeune").sum())
    return df

# ------------------------------------------------------------------ epargne (tous) -- BRUT
def gen_epargne(cfg, rng, mb):
    n = len(mb); fin = pd.Timestamp(cfg["date_fin"])
    disc = mb["lat_discipline"].values
    p_depot = np.clip(sigmoid(1.3 * disc + rng.normal(0, 0.3, n)), 0.03, 0.98)
    # tableau mois par mois (colonne 0 = il y a 11 mois, colonne 11 = mois courant) : la somme de
    # 12 Bernoulli(p) independants suit la meme loi Binomiale(12,p) que l'ancien tirage direct,
    # mais expose desormais QUELS mois ont un depot, pour aligner les mouvements generes dessus.
    mois_avec_depot = rng.random((n, 12)) < p_depot[:, None]
    # un mois ne peut etre "avec depot" que si le societaire etait deja adherent ce mois-la :
    # masquer les colonnes hors fenetre d'adherence AVANT de sommer (plutot que plafonner
    # nb_mois a l'anciennete apres coup) garde nb_mois_avec_depot_12m rigoureusement identique
    # au compte tire de mouv dans la boucle ci-dessous, qui applique deja cette meme regle.
    anciennete = mb["anciennete_societaire_mois"].values
    mois_valides = np.arange(12)[None, :] >= (12 - np.clip(anciennete, 0, 12))[:, None]
    mois_avec_depot &= mois_valides
    nb_mois = mois_avec_depot.sum(axis=1)
    solde = (cfg["depot_mensuel_median"] * (0.6 + 1.6 * sigmoid(disc)) *
             (0.5 + 0.9 * rng.random(n)) * (1 + mb["anciennete_societaire_mois"].values/120)).astype(int)
    croissance = np.round(rng.normal(0.15, 0.25, n) + 0.25 * sigmoid(disc), 3)  # tendance du solde
    volat = np.round(np.abs(rng.normal(0.3, 0.15, n)) * (1.4 - 0.6 * sigmoid(disc)), 3)
    comptes = pd.DataFrame({
        "compte_id": [f"CPT-{i:06d}" for i in range(n)], "societaire_id": mb["societaire_id"].values,
        "solde_epargne_moyen_6m": solde, "nb_mois_avec_depot_12m": nb_mois,
        "croissance_epargne_12m": croissance, "volatilite_epargne": volat,
    })

    # mouvements alignes mois par mois sur mois_avec_depot : un mois marque "avec depot" produit
    # toujours un mouvement de sens "depot" (hausse de solde) ce mois-la, jamais l'inverse. Plus
    # d'echantillon aleatoire decorrele (l'ancienne cle "k" donnait 0 a 10 mouvements sans lien
    # avec les mois effectivement marques "avec depot", d'ou des puces de regularite et un
    # graphique de mouvements incoherents entre eux cote frontend).
    mois_courant = pd.Timestamp(fin.year, fin.month, 1)
    debuts_mois = [mois_courant - pd.DateOffset(months=11 - j) for j in range(12)]
    adhesions = mb["date_adhesion"].values
    montant_base = cfg["depot_mensuel_median"] * (0.6 + 1.6 * sigmoid(disc))
    lignes = []
    for i, r in enumerate(comptes.itertuples()):
        adhesion_i = pd.Timestamp(adhesions[i])
        total_depot, jours_depot, jours_libres = 0, [], []
        for j, debut in enumerate(debuts_mois):
            if debut < adhesion_i:
                continue  # pas encore societaire ce mois-la : aucun mouvement possible
            # borne au mois calendaire, sans jamais depasser fin (mois courant partiel) : le
            # module l'exige ("Aucune date > date_fin", voir docstring en tete de fichier).
            borne_sup = min(debut + pd.DateOffset(months=1), fin + pd.Timedelta(days=1))
            jour = debut + pd.to_timedelta(int(rng.integers(0, (borne_sup - debut).days)), unit="D")
            if mois_avec_depot[i, j]:
                montant = max(int(abs(rng.normal(montant_base[i], montant_base[i] * 0.35))), 1000)
                lignes.append((f"MVT-{len(lignes):07d}", r.compte_id, jour, "depot", montant))
                total_depot += montant
                jours_depot.append(jour)
            else:
                jours_libres.append(jour)

        # aligne la pente des mouvements sur croissance_epargne_12m (la vraie variable de
        # tendance, feature du modele) : sans ce retrait correctif, un mois "avec depot" est
        # toujours positif et la courbe reconstruite cote frontend (ancree sur le solde 6 mois)
        # grimpe presque systematiquement, meme quand la tendance reelle tiree est a l'erosion.
        retrait_requis = max(total_depot - croissance[i] * solde[i], 0)
        porteurs = jours_libres or jours_depot
        if retrait_requis > 0 and porteurs:
            k = min(len(porteurs), 2)
            part = int(retrait_requis / k)
            if part >= 1000:
                for idx in rng.choice(len(porteurs), size=k, replace=False):
                    lignes.append((f"MVT-{len(lignes):07d}", r.compte_id, porteurs[idx], "retrait", part))
    mouv = pd.DataFrame(lignes, columns=["mouvement_id","compte_id","date_operation","sens","montant"])
    return comptes, mouv

# ------------------------------------------------------------------ groupes GIE (segment femme_gie)
def gen_gie(cfg, rng, mb):
    fin = pd.Timestamp(cfg["date_fin"])
    idx = np.where(mb["segment"].values == "femme_gie")[0]; rng.shuffle(idx)
    groupes, appart = [], []; qualite = {}; grp_of = np.full(len(mb), None, dtype=object)
    taille_of = np.full(len(mb), np.nan); gid = 0; i = 0
    adh = mb["date_adhesion"].values
    while i < len(idx):
        taille = int(rng.integers(cfg["taille_gie_min"], cfg["taille_gie_max"] + 1))
        membres = idx[i:i+taille]; i += taille
        if len(membres) < cfg["taille_gie_min"]: break
        g = f"GIE-{gid:04d}"; qualite[g] = rng.normal(0, 1); gid += 1
        creation = pd.Timestamp(min(adh[membres])) + pd.to_timedelta(int(rng.uniform(0, 400)), "D")
        if creation > fin: creation = fin - pd.to_timedelta(int(rng.uniform(30, 300)), "D")
        for m in membres:
            entree = max(pd.Timestamp(adh[m]), creation) + pd.to_timedelta(int(rng.uniform(0,120)),"D")
            if entree > fin: entree = fin - pd.to_timedelta(int(rng.uniform(1,90)), "D")
            sortie = None
            if rng.random() < cfg["taux_sortie_gie_annuel"] * cfg["annees_credit_observe"]:
                s = entree + pd.to_timedelta(int(rng.uniform(120, 900)), "D")
                sortie = s if s < fin else None
            role = rng.choice(["membre","presidente","tresoriere"], p=[0.84,0.08,0.08])
            appart.append((f"APP-{len(appart):06d}", g, mb.iloc[m]["societaire_id"], entree, sortie, role))
            if sortie is None: grp_of[m] = g; taille_of[m] = len(membres)
        groupes.append((g, len(membres), creation, qualite[g]))
    mb = mb.copy(); mb["gie_id"] = grp_of; mb["taille_gie"] = taille_of
    dfg = pd.DataFrame(groupes, columns=["gie_id","taille","date_creation","lat_qualite_gie"])
    dfa = pd.DataFrame(appart, columns=["appartenance_id","gie_id","societaire_id","date_entree","date_sortie","role"])
    return mb, dfg, dfa, qualite

# ------------------------------------------------------------------ choc sectoriel
def gen_choc(cfg, rng):
    fin = pd.Timestamp(cfg["date_fin"])
    mois = pd.date_range(fin - pd.DateOffset(years=cfg["annees_credit_observe"]), fin, freq="MS")
    rho, sig = cfg["secteur_autocorrelation"], cfg["secteur_choc_ecart"]
    serie = np.zeros(len(mois)); etat = 0.0
    for t in range(len(mois)):
        etat = rho * etat + rng.normal(0, sig)
        if rng.random() < cfg["secteur_episode_degradation_proba"]: etat += rng.uniform(1.0, 2.2)
        serie[t] = etat
    return pd.Series(serie, index=mois)

def choc_at(choc, date):
    i = max(0, min(choc.index.searchsorted(pd.Timestamp(date), side="right") - 1, len(choc)-1))
    return float(choc.iloc[i])

# ------------------------------------------------------------------ catalogue produits (referentiel)
def gen_produits(cfg):
    # Deterministe (aucun tirage rng) : ne consomme aucun etat aleatoire, donc ne perturbe pas la
    # sequence de tirages du reste du pipeline malgre la graine fixe. Un produit par segment
    # (typologie confirmee FUCEC-Togo/RCPB/PAMECAS, voir config.yaml).
    lignes = []
    for segment, p in cfg["produits"].items():
        lignes.append({
            "produit_id": p["produit_id"], "libelle": p["libelle"], "segment": segment,
            "type_garantie": p["type_garantie"], "montant_min": p["montant_min"],
            "montant_max": p["montant_max"], "duree_min_mois": p["duree_min_mois"],
            "duree_max_mois": p["duree_max_mois"], "taux_annuel": p["taux_annuel"],
        })
    return pd.DataFrame(lignes)

# ------------------------------------------------------------------ credits (~25% empruntent) -- BRUT
def gen_credits(cfg, rng, mb, choc, qualite, sc_std):
    fin = pd.Timestamp(cfg["date_fin"]); debut = fin - pd.DateOffset(years=cfg["annees_credit_observe"])
    C = cfg
    # selection des emprunteurs : proba croissante avec discipline + anciennete (selection realiste)
    score_sel = 0.8 * mb["lat_discipline"].values + 0.5 * z(mb["anciennete_societaire_mois"].values)
    p_emp = sigmoid(score_sel - 0.4)
    p_emp = p_emp / p_emp.mean() * C["part_emprunteurs"]
    est_emp = rng.random(len(mb)) < np.clip(p_emp, 0, 0.95)
    emp = mb[est_emp]

    lignes = []
    for r in emp.itertuples():
        # il faut avoir epargne >= epargne_min_mois avant le 1er credit
        debut_credit = max(debut, pd.Timestamp(r.date_adhesion) + pd.DateOffset(months=C["epargne_min_mois_avant_credit"]))
        if debut_credit >= fin: continue
        primo_only = r.segment == "jeune" and rng.random() < 0.6
        n_credits = 1 if primo_only else int(rng.integers(1, 6))
        # Produit du segment : borne le montant et restreint les durees choisies (catalogue,
        # voir gen_produits/config.yaml). Repli sur la liste complete si aucune duree du choix
        # global ne tombe dans les bornes du produit (ne devrait pas arriver avec le calibrage
        # actuel, garde defensive).
        produit = C["produits"][r.segment]
        duree_choix_produit = [
            d for d in C["duree_mois_choix"]
            if produit["duree_min_mois"] <= d <= produit["duree_max_mois"]
        ] or C["duree_mois_choix"]
        t0 = debut_credit; montant_ref = C["montant_median_primo"]; max_remb = 0.0; incidents = 0
        for cyc in range(1, n_credits + 1):
            if t0 >= fin: break
            ddate = t0 + pd.to_timedelta(int(rng.uniform(20, 350)), "D")
            if ddate >= fin: break
            duree = int(rng.choice(duree_choix_produit))
            plafond = max(C["montant_median_primo"], int(max_remb * C["coefficient_progression"]))
            montant = int(min(plafond, montant_ref * rng.uniform(0.7, 1.6), produit["montant_max"]))
            revenu = max(int(r.revenu_declare), 1)
            echeance = montant / duree * (1 + C["taux_interet_annuel"] * duree / 12 / duree * duree/12)
            echeance = montant / duree * 1.10
            endettement = echeance / (revenu * 0.9)
            q = qualite.get(r.gie_id, 0.0) if r.segment == "femme_gie" and r.gie_id else 0.0
            sc = choc_at(choc, ddate) / sc_std
            eps = rng.normal(0, 1)

            lp0 = (
                - C["coef_epargne_regularite"] * r.lat_discipline
                - C["coef_epargne_anciennete"] * ((r.anciennete_societaire_mois - 48)/48.0)
                - C["coef_salarie"] * (1.0 if r.segment == "salarie" else 0.0)
                - C["coef_cycle"] * (cyc - 1)/2.0
                - C["coef_anciennete"] * ((r.anciennete_societaire_mois - 60)/60.0)
                - C["coef_qualite_groupe"] * q
                + C["coef_endettement"] * np.clip(endettement, 0, 3)
                + C["coef_incidents"] * (incidents/2.0)
                + C["coef_dependants"] * ((r.nb_personnes_a_charge - 2.4)/2.0)
                + C["coef_rural"] * (1.0 if r.zone == "rural" else 0.0)
                + C["coef_jeune"] * (1.0 if r.segment == "jeune" else 0.0)
                + C["coef_agricole_choc"] * (sc if r.segment == "agricole" else 0.0)
                + C["ecart_idiosyncratique"] * eps
            )
            reveal = ddate + pd.DateOffset(months=duree); en_cours = reveal > fin
            lignes.append({
                "credit_id": f"CRD-{len(lignes):06d}", "societaire_id": r.societaire_id,
                "segment": r.segment, "produit_id": produit["produit_id"],
                "zone": r.zone, "gie_id": r.gie_id if r.segment=="femme_gie" else None,
                "date_deblocage": ddate, "date_issue": reveal, "duree_mois": duree,
                "numero_cycle": cyc, "montant_octroye": montant, "endettement": endettement,
                "est_primo": int(cyc == 1), "en_cours": en_cours, "lat_lp0": lp0,
            })
            montant_ref = montant; t0 = ddate
            # "Capacite historique" (cf. backend/solida/domain/rules/progressif.py, calculer_plafond) :
            # ne progresse qu'a partir des cycles deja resolus a date_fin, pas d'un credit encore en cours. Sans
            # cette mise a jour, max_remb restait a 0.0 pour toujours et le plafond de progression
            # ne depassait jamais montant_median_primo (100 000 FCFA), quel que soit le produit.
            if not en_cours:
                max_remb = max(max_remb, montant)
            if not en_cours and rng.random() < sigmoid(lp0):  # provision incidents pour cycle suivant
                incidents += 1
    df = pd.DataFrame(lignes).sort_values("date_deblocage").reset_index(drop=True)

    # calibration intercept sur le TAUX en souffrance (~9%), pas sur l'AUC
    resolus = ~df["en_cours"].values; lp0 = df["lat_lp0"].values; cible = C["taux_defaut_cible"]
    lo, hi = -12.0, 6.0
    for _ in range(60):
        b0 = (lo + hi)/2
        if sigmoid(b0 + lp0[resolus]).mean() > cible: hi = b0
        else: lo = b0
    b0 = (lo + hi)/2

    # tirage sequentiel avec CONTAGION GIE (defauts recents des paires -> risque focal)
    gie_hist = {}   # gie -> list (date_issue, defaut)
    defaut = np.full(len(df), 0); en_c = df["en_cours"].values
    dd = df["date_deblocage"].values; di = df["date_issue"].values
    gid_arr = df["gie_id"].values; seg = df["segment"].values
    for k in range(len(df)):
        contag = 0.0
        if seg[k] == "femme_gie" and gid_arr[k] is not None:
            h = gie_hist.get(gid_arr[k], [])
            fen = pd.Timestamp(dd[k]) - pd.DateOffset(months=C["fenetre_contagion_mois"])
            recent = [d for (t, d) in h if fen <= t < pd.Timestamp(dd[k])]
            if recent: contag = C["coef_contagion_gie"] * (np.mean(recent) - cible)
        p = sigmoid(b0 + lp0[k] + contag)
        d = 0 if en_c[k] else int(rng.random() < p)
        defaut[k] = -1 if en_c[k] else d
        if not en_c[k] and gid_arr[k] is not None:
            gie_hist.setdefault(gid_arr[k], []).append((pd.Timestamp(di[k]), d))
    df["defaut"] = defaut
    df["statut"] = np.where(en_c, "en_cours", np.where(defaut == 1, "en_souffrance", "solde"))

    # jours de retard (champ BRUT du SIG) : correle au risque, meme sans souffrance
    zr = z(df["lat_lp0"].values)
    jr = np.where(defaut == 1, 90 + rng.exponential(70, len(df)),
                  np.clip(rng.normal(18 * sigmoid(zr), 12), 0, 88))
    df["jours_retard_max"] = np.where(defaut < 0, np.nan, np.round(jr, 0))
    return df, emp

# ------------------------------------------------------------------ garanties (BRUT)
def gen_garanties(cfg, rng, mb, credits, comptes, appart):
    solde = comptes.set_index("societaire_id")["solde_epargne_moyen_6m"].to_dict()
    membres_gie = appart.groupby("gie_id")["societaire_id"].apply(list).to_dict()
    lignes = []
    for r in credits.itertuples():
        if r.segment == "femme_gie" and r.gie_id:
            pairs = [m for m in membres_gie.get(r.gie_id, []) if m != r.societaire_id]
            if pairs:
                garant = rng.choice(pairs); appelee = (r.defaut == 1) and (rng.random() < 0.6)
                lignes.append((f"GAR-{len(lignes):06d}", r.credit_id, "caution_solidaire_gie",
                    garant, r.societaire_id, int(r.montant_octroye*0.5),
                    pd.Timestamp(r.date_deblocage), bool(appelee))); continue
        # sinon : epargne nantie (garantie reelle, pas de lien interpersonnel)
        montant_nanti = int(min(solde.get(r.societaire_id, 0), r.montant_octroye))
        lignes.append((f"GAR-{len(lignes):06d}", r.credit_id, "epargne_nantie",
            None, r.societaire_id, montant_nanti, pd.Timestamp(r.date_deblocage), False))
    return pd.DataFrame(lignes, columns=["garantie_id","credit_id","type_garantie",
        "garant_societaire_id","beneficiaire_societaire_id","montant_garanti","date_engagement","garantie_appelee"])

def injecter_manquants(cfg, rng, mb):
    mb = mb.copy()
    m = np.where(mb["zone"].values == "rural", cfg["manquant_revenu_rural"], cfg["manquant_revenu_urbain"])
    mb.loc[rng.random(len(mb)) < m, "revenu_declare"] = np.nan
    mb.loc[rng.random(len(mb)) < cfg["manquant_education"], "niveau_education"] = None
    return mb

def controles(cfg, mb, comptes, credits, gie, appart, garanties, mouv, produits):
    fin = pd.Timestamp(cfg["date_fin"]); r = {}
    res = credits[credits["defaut"] >= 0]
    r["taux_souffrance_resolus"] = round(res["defaut"].mean(), 4)
    r["part_credits_en_cours"] = round((credits["defaut"] < 0).mean(), 4)
    r["part_membres_emprunteurs"] = round(credits["societaire_id"].nunique() / len(mb), 4)
    r["part_credits_gie"] = round((credits["segment"] == "femme_gie").mean(), 4)
    r["part_credits_salarie"] = round((credits["segment"] == "salarie").mean(), 4)
    r["produits_orphelins"] = int((~credits["produit_id"].isin(produits["produit_id"])).sum())
    dep = 0
    for s, col in [(mb,"date_adhesion"),(credits,"date_deblocage"),(gie,"date_creation"),
                   (appart,"date_entree"),(mouv,"date_operation"),(garanties,"date_engagement")]:
        if len(s): dep += int((pd.to_datetime(s[col]) > fin).sum())
    if len(appart): dep += int((pd.to_datetime(appart["date_sortie"].dropna()) > fin).sum())
    r["evenements_apres_date_fin"] = dep
    r["anciennete_min_mois"] = int(mb["anciennete_societaire_mois"].min())
    r["anciennete_max_mois"] = int(mb["anciennete_societaire_mois"].max())
    r["n_membres"] = len(mb); r["n_credits"] = len(credits); r["n_gie"] = len(gie)
    r["n_garanties_epargne_nantie"] = int((garanties["type_garantie"]=="epargne_nantie").sum())
    r["n_garanties_caution_gie"] = int((garanties["type_garantie"]=="caution_solidaire_gie").sum())
    r["cautions_gie_appelees"] = int(garanties["garantie_appelee"].sum())
    return r

if __name__ == "__main__":
    cfg = charger_config(); rng = np.random.default_rng(cfg["graine"])
    mb = gen_membres(cfg, rng)
    comptes, mouv = gen_epargne(cfg, rng, mb)
    mb, gie, appart, qualite = gen_gie(cfg, rng, mb)
    choc = gen_choc(cfg, rng); sc_std = float(np.std(choc.values))
    credits, emp = gen_credits(cfg, rng, mb, choc, qualite, sc_std)
    garanties = gen_garanties(cfg, rng, mb, credits, comptes, appart)
    mb = injecter_manquants(cfg, rng, mb)
    produits = gen_produits(cfg)
    rap = controles(cfg, mb, comptes, credits, gie, appart, garanties, mouv, produits)

    out = RACINE / "sorties"; out.mkdir(exist_ok=True)
    def sans_lat(d): return d[[c for c in d.columns if not c.startswith("lat_")]]
    sans_lat(mb).to_parquet(out / "societaires.parquet")
    sans_lat(credits).to_parquet(out / "credits.parquet")
    sans_lat(gie).to_parquet(out / "groupes_gie.parquet")
    appart.to_parquet(out / "appartenances_gie.parquet")
    comptes.to_parquet(out / "comptes_epargne.parquet")
    mouv.to_parquet(out / "mouvements_epargne.parquet")
    garanties.to_parquet(out / "garanties.parquet")
    produits.to_parquet(out / "produits_credit.parquet")
    choc.to_frame("choc_sectoriel").to_parquet(out / "choc_secteur.parquet")
    credits.to_parquet(out / "_credits_latents.parquet")   # avec lat_ pour la validation
    mb.to_parquet(out / "_societaires_latents.parquet")

    print("=== RAPPORT COHERENCE / DATES (logique COOPEC) ===")
    for k, v in rap.items(): print(f"  {k:30s}: {v}")
