"""Generateur CORE-SIM SOLIDA -- decisions terrain J1-05 a J1-13.

Les variables d'issue (paiements, retards, statut et defaut) sont produites apres
le decaissement. Elles ne participent jamais au mecanisme de risque a l'octroi.
Toutes les anciennetes de ce mecanisme sont calculees a la date du credit.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

RACINE = Path(__file__).resolve().parent.parent

# Liste explicite et testee : ni age, ni issue post-decaissement, ni action de suivi.
VARIABLES_RISQUE_OCTROI = (
    "regularite_epargne",
    "anciennete_epargne_a_octroi",
    "ratio_garantie",
    "segment_salarie",
    "numero_cycle",
    "anciennete_societaire_a_octroi",
    "qualite_groupe",
    "endettement",
    "nb_personnes_a_charge",
    "zone_rurale",
    "segment_jeune",
    "choc_agricole",
)

PATRONYMES = [
    "ADJOVI",
    "AGBEKO",
    "AGBODJAN",
    "AKAKPO",
    "AMEGAN",
    "AMOUZOU",
    "ATSU",
    "AYITE",
    "DOSSOU",
    "EKUE",
    "FOLI",
    "GAKPE",
    "KODJO",
    "KOUASSI",
    "KPODAR",
    "LAWSON",
    "MENSAH",
    "NYAVOR",
    "SODJI",
    "SOSSOU",
    "TCHALLA",
    "TETTEH",
    "ZANOU",
    "ABALO",
    "ALASSANI",
    "BAKARI",
    "DJAGBA",
    "HODABALO",
    "LARE",
    "PIYABALO",
    "TCHASSANTI",
    "WALLA",
    "ESSOZIMNA",
    "AMEVO",
    "GNIMASSOU",
    "KANLANFEI",
    "BATABA",
    "AKUE",
    "DEGBEVI",
    "OURO",
    "SAMBIANI",
    "TCHAGNAO",
    "BASSABI",
    "AZIABLI",
    "KOSSIVI",
    "DABLA",
    "AFANOU",
    "GBIKPI",
]
PRENOMS_M = [
    "Kokou",
    "Kofi",
    "Komla",
    "Kwami",
    "Yao",
    "Kodjo",
    "Kossi",
    "Selom",
    "Elom",
    "Edem",
    "Mawuli",
    "Senyo",
    "Delali",
    "Koffi",
    "Komi",
    "Folly",
    "Essohanam",
    "Amevo",
    "Sena",
    "Kossivi",
    "Mensah",
    "Ayao",
]
PRENOMS_F = [
    "Akouvi",
    "Ama",
    "Afi",
    "Adjo",
    "Adjovi",
    "Akossiwa",
    "Abra",
    "Essi",
    "Adzo",
    "Dede",
    "Enyonam",
    "Ablavi",
    "Afiwa",
    "Akpene",
    "Sitsope",
    "Mawusi",
    "Yawa",
    "Dela",
    "Akuvi",
    "Elolo",
    "Sedjro",
    "Afia",
]


def charger_config(p=RACINE / "config/config.yaml"):
    with Path(p).open(encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def z(a):
    valeurs = np.asarray(a, dtype=float)
    ecart = valeurs.std()
    return (valeurs - valeurs.mean()) / (ecart if ecart > 1e-9 else 1.0)


def noms(rng, sexes):
    utilises = set()
    resultat = []
    for sexe in sexes:
        base = PRENOMS_F if sexe == "F" else PRENOMS_M
        for _ in range(500):
            patronyme = rng.choice(PATRONYMES)
            prenom = rng.choice(base)
            second = f" {rng.choice(PRENOMS_M + PRENOMS_F)}" if rng.random() < 0.4 else ""
            nom = f"{patronyme} {prenom}{second}"
            if nom not in utilises:
                break
        else:
            nom = (
                f"{patronyme} {prenom} {rng.choice(PRENOMS_M + PRENOMS_F)} "
                f"{rng.choice(PRENOMS_M + PRENOMS_F)}"
            )
        utilises.add(nom)
        resultat.append(nom)
    return resultat


def tirer_anciennetes_mois(rng, n, maximum_mois):
    """Produit exactement les trois strates 15/25/60, a l'arrondi d'effectif pres."""
    n_court = int(round(n * 0.15))
    n_moyen = int(round(n * 0.25))
    n_long = n - n_court - n_moyen
    valeurs = np.concatenate(
        [
            rng.integers(3, 6, n_court),
            rng.integers(6, 12, n_moyen),
            rng.integers(12, maximum_mois + 1, n_long),
        ]
    )
    rng.shuffle(valeurs)
    return valeurs.astype(int)


def mois_ecoules(debut, fin):
    debut = pd.Timestamp(debut)
    fin = pd.Timestamp(fin)
    mois = (fin.year - debut.year) * 12 + fin.month - debut.month
    return max(mois - int(fin.day < debut.day), 0)


def gen_membres(cfg, rng):
    n = int(cfg["n_membres"])
    fin = pd.Timestamp(cfg["date_fin"])
    anciennetes = tirer_anciennetes_mois(rng, n, int(cfg["anciennete_max_annees"] * 12))
    adhesions = pd.Series(
        [fin - pd.DateOffset(months=int(mois)) for mois in anciennetes], dtype="datetime64[ns]"
    )

    segments = list(cfg["segments"])
    poids = np.array([cfg["segments"][segment] for segment in segments], dtype=float)
    poids /= poids.sum()
    segment = rng.choice(segments, n, p=poids)
    sexe = np.where(segment == "femme_gie", "F", rng.choice(["F", "M"], n, p=[0.55, 0.45]))
    zone = rng.choice(cfg["zones"], n, p=cfg["zones_poids"])
    zone = np.where((segment == "agricole") & (rng.random(n) < 0.6), "rural", zone)

    fiabilite = rng.normal(0, 1, n)
    discipline = 0.6 * fiabilite + 0.8 * rng.normal(0, 1, n)
    education_latente = 0.6 * fiabilite + rng.normal(0, 0.9, n)
    niveaux = np.array(["aucun", "primaire", "secondaire", "superieur"])
    education = niveaux[np.clip(np.digitize(education_latente, [-0.8, 0.1, 1.0]), 0, 3)]
    ages = rng.integers(18, 81, n)
    ages[segment == "jeune"] = rng.integers(18, 30, int((segment == "jeune").sum()))

    return pd.DataFrame(
        {
            "societaire_id": [f"SOC-{i:06d}" for i in range(n)],
            "numero_membre": [f"{100000 + i:06d}" for i in range(n)],
            "nom_complet": noms(rng, sexe),
            "caisse_id": [f"CAI-{i:02d}" for i in rng.integers(0, cfg["n_caisses"], n)],
            "date_adhesion": adhesions,
            "anciennete_societaire_mois": anciennetes,
            "segment": segment,
            "age": ages,
            "sexe": sexe,
            "statut_matrimonial": rng.choice(
                ["celibataire", "marie", "veuf", "divorce"], n, p=[0.28, 0.58, 0.08, 0.06]
            ),
            "zone": zone,
            "nb_personnes_a_charge": rng.poisson(2.4, n),
            "niveau_education": education,
            "parts_sociales": rng.integers(5_000, 60_000, n),
            "revenu_declare": rng.lognormal(np.log(85_000), 0.5, n).astype(int),
            "lat_fiabilite": fiabilite,
            "lat_discipline": discipline,
        }
    )


def gen_epargne_base(cfg, rng, membres):
    """Genere les depots/retraits depuis l'ouverture et les soldes journaliers utiles."""
    fin = pd.Timestamp(cfg["date_fin"])
    mouvements = []
    historiques = {}
    ordre = 0
    for membre in membres.itertuples():
        compte_id = membre.societaire_id.replace("SOC", "CPT")
        probabilite_depot = float(np.clip(sigmoid(1.3 * membre.lat_discipline), 0.08, 0.96))
        montant_typique = cfg["depot_mensuel_median"] * (0.6 + 1.6 * sigmoid(membre.lat_discipline))
        solde = 0
        historique = []
        ouverture = pd.Timestamp(membre.date_adhesion)
        for debut_mois in pd.date_range(ouverture, fin, freq="MS"):
            borne = min(debut_mois + pd.DateOffset(months=1), fin + pd.Timedelta(days=1))
            jours = max((borne - debut_mois).days, 1)
            jour_depot = None
            if rng.random() < probabilite_depot:
                date = debut_mois + pd.Timedelta(days=int(rng.integers(0, jours)))
                jour_depot = int((date - debut_mois).days)
                montant = max(int(abs(rng.normal(montant_typique, montant_typique * 0.35))), 1_000)
                solde += montant
                mouvements.append(
                    {
                        "compte_id": compte_id,
                        "date_operation": date,
                        "type_operation": "depot",
                        "sens": "depot",
                        "montant": montant,
                        "credit_id": None,
                        "_ordre": ordre,
                    }
                )
                historique.append((date, ordre, solde))
                ordre += 1
            if solde > 0 and rng.random() < cfg["probabilite_retrait_mensuel"]:
                # Si le retrait utilise le depot du mois, sa date doit lui etre
                # posterieure afin que le journal brut et le solde soient coherents.
                premier_jour = jour_depot if jour_depot is not None else 0
                date = debut_mois + pd.Timedelta(days=int(rng.integers(premier_jour, jours)))
                plafond = max(int(solde * rng.uniform(0.05, 0.35)), 1)
                montant = min(max(int(rng.uniform(1_000, max(plafond, 1_001))), 1_000), solde)
                solde -= montant
                mouvements.append(
                    {
                        "compte_id": compte_id,
                        "date_operation": date,
                        "type_operation": "retrait",
                        "sens": "retrait",
                        "montant": montant,
                        "credit_id": None,
                        "_ordre": ordre,
                    }
                )
                historique.append((date, ordre, solde))
                ordre += 1
        historiques[membre.societaire_id] = sorted(
            historique, key=lambda valeur: (valeur[0], valeur[1])
        )
    return mouvements, historiques, ordre


def solde_minimal_disponible(historique, debut, fin):
    """Minimum du solde libre entre deux dates, apres les operations du jour de debut."""
    debut = pd.Timestamp(debut)
    fin = pd.Timestamp(fin)
    avant = [solde for date, _, solde in historique if date <= debut]
    courant = avant[-1] if avant else 0
    minimum = courant
    for date, _, solde in historique:
        if debut < date <= fin:
            minimum = min(minimum, solde)
    return max(int(minimum), 0)


def gen_gie(cfg, rng, membres):
    fin = pd.Timestamp(cfg["date_fin"])
    indices = np.where(membres["segment"].values == "femme_gie")[0]
    rng.shuffle(indices)
    groupes, appartenances, qualite = [], [], {}
    groupe_de = np.full(len(membres), None, dtype=object)
    taille_de = np.full(len(membres), np.nan)
    curseur = 0
    numero = 0
    while curseur < len(indices):
        taille = int(rng.integers(cfg["taille_gie_min"], cfg["taille_gie_max"] + 1))
        indices_membres = indices[curseur : curseur + taille]
        curseur += taille
        if len(indices_membres) < cfg["taille_gie_min"]:
            break
        gie_id = f"GIE-{numero:04d}"
        numero += 1
        qualite[gie_id] = float(rng.normal(0, 1))
        creation = pd.Timestamp(membres.iloc[indices_membres]["date_adhesion"].min())
        creation += pd.Timedelta(days=int(rng.uniform(0, 120)))
        creation = min(creation, fin)
        for index in indices_membres:
            membre = membres.iloc[index]
            entree = min(max(pd.Timestamp(membre.date_adhesion), creation), fin)
            sortie = None
            if rng.random() < cfg["taux_sortie_gie_annuel"]:
                candidate = entree + pd.Timedelta(days=int(rng.uniform(120, 900)))
                sortie = candidate if candidate <= fin else None
            role = rng.choice(["membre", "presidente", "tresoriere"], p=[0.84, 0.08, 0.08])
            appartenances.append(
                (
                    f"APP-{len(appartenances):06d}",
                    gie_id,
                    membre.societaire_id,
                    entree,
                    sortie,
                    role,
                )
            )
            if sortie is None:
                groupe_de[index] = gie_id
                taille_de[index] = len(indices_membres)
        groupes.append((gie_id, len(indices_membres), creation, qualite[gie_id]))
    resultat = membres.copy()
    resultat["gie_id"] = groupe_de
    resultat["taille_gie"] = taille_de
    return (
        resultat,
        pd.DataFrame(groupes, columns=["gie_id", "taille", "date_creation", "lat_qualite_gie"]),
        pd.DataFrame(
            appartenances,
            columns=[
                "appartenance_id",
                "gie_id",
                "societaire_id",
                "date_entree",
                "date_sortie",
                "role",
            ],
        ),
        qualite,
    )


def gen_choc(cfg, rng):
    fin = pd.Timestamp(cfg["date_fin"])
    debut = fin - pd.DateOffset(years=cfg["anciennete_max_annees"])
    mois = pd.date_range(debut, fin, freq="MS")
    serie = np.zeros(len(mois))
    etat = 0.0
    for index in range(len(mois)):
        etat = cfg["secteur_autocorrelation"] * etat + rng.normal(0, cfg["secteur_choc_ecart"])
        if rng.random() < cfg["secteur_episode_degradation_proba"]:
            etat += rng.uniform(1.0, 2.2)
        serie[index] = etat
    return pd.Series(serie, index=mois)


def choc_a_date(choc, date):
    index = max(
        0, min(choc.index.searchsorted(pd.Timestamp(date), side="right") - 1, len(choc) - 1)
    )
    return float(choc.iloc[index])


def gen_produits(cfg):
    lignes = []
    for segment, produit in cfg["produits"].items():
        taux_min = float(produit["taux_annuel_min"])
        taux_max = float(produit["taux_annuel_max"])
        lignes.append(
            {
                "produit_id": produit["produit_id"],
                "libelle": produit["libelle"],
                "segment": segment,
                "type_garantie": produit["type_garantie"],
                "montant_min": produit["montant_min"],
                "montant_max": produit["montant_max"],
                "duree_min_mois": produit["duree_min_mois"],
                "duree_max_mois": produit["duree_max_mois"],
                "taux_annuel_min": taux_min,
                "taux_annuel_max": taux_max,
                "taux_annuel": (taux_min + taux_max) / 2,
            }
        )
    return pd.DataFrame(lignes)


def periodicites_compatibles(duree_mois):
    compatibles = ["hebdomadaire", "mensuelle"]
    if duree_mois % 3 == 0:
        compatibles.append("trimestrielle")
    if duree_mois % 6 == 0:
        compatibles.append("semestrielle")
    if duree_mois % 12 == 0:
        compatibles.append("annuelle")
    return compatibles


def tirer_periodicite(cfg, rng, duree_mois):
    compatibles = periodicites_compatibles(duree_mois)
    poids = np.array([cfg["periodicites_remboursement"][p] for p in compatibles], dtype=float)
    poids /= poids.sum()
    return str(rng.choice(compatibles, p=poids))


def tirer_montant_credit(cfg, rng, epargne_libre_disponible=None):
    minimum = int(cfg["montant_synthetique_min"])
    maximum = int(cfg["montant_synthetique_max"])
    if epargne_libre_disponible is not None:
        maximum = min(maximum, int(epargne_libre_disponible / cfg["nantissement_taux_min"]))
    if maximum < minimum:
        return None
    return int(round(np.exp(rng.uniform(np.log(minimum), np.log(maximum)))))


def _nombre_echeances(duree_mois, periodicite):
    if periodicite == "hebdomadaire":
        return max(int(round(duree_mois * 52 / 12)), 1)
    pas = {"mensuelle": 1, "trimestrielle": 3, "semestrielle": 6, "annuelle": 12}[periodicite]
    return duree_mois // pas


def _dates_echeances(date_deblocage, duree_mois, periodicite, nombre):
    date_deblocage = pd.Timestamp(date_deblocage)
    maturite = date_deblocage + pd.DateOffset(months=int(duree_mois))
    if periodicite == "hebdomadaire":
        dates = [date_deblocage + pd.Timedelta(weeks=i) for i in range(1, nombre)]
        return dates + [maturite]
    pas = {"mensuelle": 1, "trimestrielle": 3, "semestrielle": 6, "annuelle": 12}[periodicite]
    return [date_deblocage + pd.DateOffset(months=pas * i) for i in range(1, nombre + 1)]


def construire_echeancier_theorique(montant, taux_annuel, duree_mois, periodicite, date_deblocage):
    """Echeances constantes; interets calcules a chaque periode sur le capital restant."""
    frequences = {
        "hebdomadaire": 52,
        "mensuelle": 12,
        "trimestrielle": 4,
        "semestrielle": 2,
        "annuelle": 1,
    }
    nombre = _nombre_echeances(int(duree_mois), periodicite)
    taux_periode = float(taux_annuel) / frequences[periodicite]
    paiement = (
        montant / nombre
        if taux_periode == 0
        else montant * taux_periode / (1 - (1 + taux_periode) ** -nombre)
    )
    dates = _dates_echeances(date_deblocage, int(duree_mois), periodicite, nombre)
    capital_restant = float(montant)
    lignes = []
    for numero, date in enumerate(dates, start=1):
        interet = capital_restant * taux_periode
        capital = capital_restant if numero == nombre else paiement - interet
        montant_prevu = int(round(capital + interet))
        capital_restant = max(capital_restant - capital, 0.0)
        lignes.append(
            {
                "numero_echeance": numero,
                "date_echeance_prevue": pd.Timestamp(date),
                "montant_prevu": montant_prevu,
                "montant_capital": int(round(capital)),
                "montant_interet": int(round(interet)),
                "capital_restant_du": int(round(capital_restant)),
            }
        )
    total = int(sum(ligne["montant_prevu"] for ligne in lignes))
    return lignes, total, total / float(duree_mois)


def ratio_endettement(charge_mensualisee, revenu_declare):
    return float(charge_mensualisee) / max(float(revenu_declare), 1.0)


def effet_endettement(ratio, seuil, coefficient):
    """Pente coefficient sous le seuil, puis pente double sur la portion excedentaire."""
    ratio = max(float(ratio), 0.0)
    sous_seuil = min(ratio, float(seuil))
    depassement = max(ratio - float(seuil), 0.0)
    return float(coefficient) * sous_seuil + 2 * float(coefficient) * depassement


def _tirer_taux(rng, produit):
    minimum = float(produit["taux_annuel_min"])
    maximum = float(produit["taux_annuel_max"])
    return minimum if minimum == maximum else float(rng.uniform(minimum, maximum))


def gen_credits(cfg, rng, membres, choc, qualite, historiques):
    fin = pd.Timestamp(cfg["date_fin"])
    score_selection = 0.8 * membres["lat_discipline"].values + 0.5 * z(
        membres["anciennete_societaire_mois"].values
    )
    probabilite = sigmoid(score_selection - 0.4)
    probabilite = probabilite / probabilite.mean() * cfg["part_emprunteurs"]
    emprunteurs = membres[rng.random(len(membres)) < np.clip(probabilite, 0, 0.95)]
    ecart_choc = max(float(np.std(choc.values)), 1e-9)
    lignes = []

    for membre in emprunteurs.itertuples():
        produit = cfg["produits"][membre.segment]
        choix_duree = [
            duree
            for duree in cfg["duree_mois_choix"]
            if produit["duree_min_mois"] <= duree <= produit["duree_max_mois"]
        ]
        premiere_date = pd.Timestamp(membre.date_adhesion) + pd.DateOffset(
            months=cfg["epargne_min_mois_avant_credit"]
        )
        if premiere_date >= fin:
            continue
        n_credits = (
            1 if membre.segment == "jeune" and rng.random() < 0.6 else int(rng.integers(1, 6))
        )
        date_possible = premiere_date
        for cycle in range(1, n_credits + 1):
            marge_jours = max((fin - date_possible).days, 0)
            if marge_jours == 0:
                break
            date_deblocage = date_possible + pd.Timedelta(
                days=int(rng.integers(0, min(marge_jours, 181)))
            )
            if date_deblocage >= fin:
                break
            duree = int(rng.choice(choix_duree))
            date_issue = date_deblocage + pd.DateOffset(months=duree)
            periodicite = tirer_periodicite(cfg, rng, duree)
            taux_annuel = _tirer_taux(rng, produit)

            disponible = None
            if membre.segment != "femme_gie":
                disponible = solde_minimal_disponible(
                    historiques[membre.societaire_id], date_deblocage, min(date_issue, fin)
                )
            montant = tirer_montant_credit(cfg, rng, disponible)
            if montant is None:
                break

            taux_nantissement = 0.0
            montant_nanti = 0
            if membre.segment != "femme_gie":
                taux_maximum = min(cfg["nantissement_taux_max"], disponible / montant)
                if taux_maximum < cfg["nantissement_taux_min"]:
                    break
                taux_nantissement = float(rng.uniform(cfg["nantissement_taux_min"], taux_maximum))
                minimum_nanti = int(np.ceil(montant * cfg["nantissement_taux_min"]))
                maximum_nanti = min(
                    int(np.floor(montant * cfg["nantissement_taux_max"])), int(disponible)
                )
                if maximum_nanti < minimum_nanti:
                    break
                montant_nanti = int(
                    np.clip(round(montant * taux_nantissement), minimum_nanti, maximum_nanti)
                )
                taux_nantissement = montant_nanti / montant

            _, total, charge = construire_echeancier_theorique(
                montant, taux_annuel, duree, periodicite, date_deblocage
            )
            endettement = ratio_endettement(charge, membre.revenu_declare)
            anciennete_octroi = mois_ecoules(membre.date_adhesion, date_deblocage)
            qualite_groupe = qualite.get(membre.gie_id, 0.0) if membre.gie_id else 0.0
            choc_standardise = choc_a_date(choc, date_deblocage) / ecart_choc
            ratio_garantie = montant_nanti / montant if montant else 0.0
            lp0 = (
                -cfg["coef_epargne_regularite"] * membre.lat_discipline
                - cfg["coef_epargne_anciennete"] * ((anciennete_octroi - 48) / 48.0)
                - cfg["coef_ratio_garantie"] * ratio_garantie
                - cfg["coef_salarie"] * (membre.segment == "salarie")
                - cfg["coef_cycle"] * ((cycle - 1) / 2.0)
                - cfg["coef_anciennete"] * ((anciennete_octroi - 60) / 60.0)
                - cfg["coef_qualite_groupe"] * qualite_groupe
                + effet_endettement(endettement, cfg["seuil_endettement"], cfg["coef_endettement"])
                + cfg["coef_dependants"] * ((membre.nb_personnes_a_charge - 2.4) / 2.0)
                + cfg["coef_rural"] * (membre.zone == "rural")
                + cfg["coef_jeune"] * (membre.segment == "jeune")
                + cfg["coef_agricole_choc"]
                * (choc_standardise if membre.segment == "agricole" else 0.0)
                + cfg["ecart_idiosyncratique"] * rng.normal(0, 1)
            )
            lignes.append(
                {
                    "societaire_id": membre.societaire_id,
                    "segment": membre.segment,
                    "produit_id": produit["produit_id"],
                    "zone": membre.zone,
                    "gie_id": membre.gie_id if membre.segment == "femme_gie" else None,
                    "date_deblocage": date_deblocage,
                    "date_issue": date_issue,
                    "duree_mois": duree,
                    "numero_cycle": cycle,
                    "montant_octroye": montant,
                    "taux_annuel": taux_annuel,
                    "total_a_rembourser": total,
                    "charge_mensualisee": charge,
                    "periodicite_remboursement": periodicite,
                    "endettement": endettement,
                    "est_primo": int(cycle == 1),
                    # La cible J+30 n'est resolue que si toute sa fenetre
                    # d'observation est anterieure a la date de coupure.
                    "en_cours": date_issue + pd.Timedelta(days=30) > fin,
                    "lat_lp0": float(lp0),
                    "lat_montant_nanti": montant_nanti,
                    "lat_taux_nantissement": taux_nantissement,
                }
            )
            # Les cycles ne se chevauchent pas. Aucun coefficient de progression de montant.
            date_possible = date_issue
            if date_issue + pd.Timedelta(days=30) > fin:
                break

    colonnes = [
        "societaire_id",
        "segment",
        "produit_id",
        "zone",
        "gie_id",
        "date_deblocage",
        "date_issue",
        "duree_mois",
        "numero_cycle",
        "montant_octroye",
        "taux_annuel",
        "total_a_rembourser",
        "charge_mensualisee",
        "periodicite_remboursement",
        "endettement",
        "est_primo",
        "en_cours",
        "lat_lp0",
        "lat_montant_nanti",
        "lat_taux_nantissement",
    ]
    if not lignes:
        return pd.DataFrame(columns=colonnes), emprunteurs
    credits = pd.DataFrame(lignes).sort_values("date_deblocage").reset_index(drop=True)

    resolus = ~credits["en_cours"].to_numpy(dtype=bool)
    lp0 = credits["lat_lp0"].to_numpy()
    borne_basse, borne_haute = -12.0, 6.0
    if resolus.any():
        for _ in range(60):
            intercept = (borne_basse + borne_haute) / 2
            if sigmoid(intercept + lp0[resolus]).mean() > cfg["taux_defaut_cible"]:
                borne_haute = intercept
            else:
                borne_basse = intercept
    intercept = (borne_basse + borne_haute) / 2
    tirages = rng.random(len(credits)) < sigmoid(intercept + lp0)
    credits["defaut"] = np.where(credits["en_cours"], -1, tirages.astype(int))

    # Une nantie d'un credit en souffrance demeure bloquee : aucun cycle ulterieur n'est emis.
    conserver = np.ones(len(credits), dtype=bool)
    for _, indices in credits.groupby("societaire_id", sort=False).groups.items():
        defaut_deja_survenu = False
        for index in sorted(indices, key=lambda i: credits.at[i, "date_deblocage"]):
            if defaut_deja_survenu:
                conserver[index] = False
            elif credits.at[index, "defaut"] == 1:
                defaut_deja_survenu = True
    credits = credits[conserver].sort_values("date_deblocage").reset_index(drop=True)
    credits.insert(0, "credit_id", [f"CRD-{i:06d}" for i in range(len(credits))])
    credits["statut"] = np.where(
        credits["en_cours"], "en_cours", np.where(credits["defaut"] == 1, "en_souffrance", "solde")
    )
    return credits, emprunteurs


def gen_echeances(cfg, rng, credits):
    fin = pd.Timestamp(cfg["date_fin"])
    lignes = []
    retards_max = {}
    for credit in credits.itertuples():
        theorie, _, _ = construire_echeancier_theorique(
            credit.montant_octroye,
            credit.taux_annuel,
            credit.duree_mois,
            credit.periodicite_remboursement,
            credit.date_deblocage,
        )
        delai_cible = 0
        index_cible = None
        dates_payables = [
            ligne["date_echeance_prevue"]
            for ligne in theorie
            if ligne["date_echeance_prevue"] <= fin
        ]
        if dates_payables:
            maximum_possible = max((fin - date).days for date in dates_payables)
            if credit.defaut == 1:
                delai_cible = min(int(30 + rng.exponential(70)), maximum_possible)
                delai_cible = max(delai_cible, 30)
            elif credit.defaut == 0:
                delai_cible = min(int(rng.exponential(4)), 29, maximum_possible)
            eligibles = [
                i
                for i, ligne in enumerate(theorie)
                if (fin - ligne["date_echeance_prevue"]).days >= delai_cible
            ]
            if eligibles:
                index_cible = int(rng.choice(eligibles))

        retards = []
        for index, ligne in enumerate(theorie):
            date_prevue = ligne["date_echeance_prevue"]
            date_reelle = pd.NaT
            montant_paye = np.nan
            jours_retard = np.nan
            if date_prevue <= fin:
                marge = max((fin - date_prevue).days, 0)
                retard = (
                    delai_cible if index == index_cible else int(rng.integers(0, min(5, marge) + 1))
                )
                retard = min(retard, marge)
                date_reelle = date_prevue + pd.Timedelta(days=retard)
                montant_paye = ligne["montant_prevu"]
                jours_retard = retard
                retards.append(retard)
            niveau = "groupe" if credit.segment == "femme_gie" else "individuel"
            lignes.append(
                {
                    "echeance_id": f"ECH-{len(lignes):08d}",
                    "credit_id": credit.credit_id,
                    "numero_echeance": ligne["numero_echeance"],
                    "date_echeance_prevue": date_prevue,
                    "date_paiement_reelle": date_reelle,
                    "montant_prevu": ligne["montant_prevu"],
                    "montant_paye": montant_paye,
                    "montant_capital": ligne["montant_capital"],
                    "montant_interet": ligne["montant_interet"],
                    "capital_restant_du": ligne["capital_restant_du"],
                    "jours_retard": jours_retard,
                    "alerte_operationnelle": bool(pd.notna(jours_retard) and jours_retard >= 1),
                    "niveau_enregistrement": niveau,
                    "groupe_id": credit.gie_id if niveau == "groupe" else None,
                    "societaire_id": None if niveau == "groupe" else credit.societaire_id,
                }
            )
        retards_max[credit.credit_id] = max(retards) if retards else np.nan
    echeances = pd.DataFrame(lignes)
    resultat = credits.copy()
    resultat["jours_retard_max"] = resultat["credit_id"].map(retards_max)
    resultat.loc[resultat["en_cours"], "jours_retard_max"] = np.nan
    return resultat, echeances


def gen_garanties(credits, appartenances, rng):
    membres_gie = appartenances.groupby("gie_id")["societaire_id"].apply(list).to_dict()
    lignes = []
    for credit in credits.itertuples():
        if credit.segment == "femme_gie" and credit.gie_id:
            pairs = [
                membre
                for membre in membres_gie.get(credit.gie_id, [])
                if membre != credit.societaire_id
            ]
            garant = rng.choice(pairs) if pairs else None
            montant = int(credit.montant_octroye * 0.5)
            type_garantie = "caution_solidaire_gie"
            appelee = bool(credit.defaut == 1 and rng.random() < 0.6)
            date_liberation = pd.NaT
        else:
            garant = None
            montant = int(credit.lat_montant_nanti)
            type_garantie = "epargne_nantie"
            appelee = False
            date_liberation = credit.date_issue if credit.statut == "solde" else pd.NaT
        lignes.append(
            {
                "garantie_id": f"GAR-{len(lignes):06d}",
                "credit_id": credit.credit_id,
                "type_garantie": type_garantie,
                "garant_societaire_id": garant,
                "beneficiaire_societaire_id": credit.societaire_id,
                "montant_garanti": montant,
                "taux_couverture": montant / credit.montant_octroye,
                "date_engagement": credit.date_deblocage,
                "date_liberation": date_liberation,
                "garantie_appelee": appelee,
            }
        )
    return pd.DataFrame(lignes)


def ajouter_mouvements_nantissement(mouvements, credits, ordre_initial):
    ordre = ordre_initial
    resultat = list(mouvements)
    for credit in credits.itertuples():
        montant = int(credit.lat_montant_nanti)
        if montant <= 0:
            continue
        compte_id = credit.societaire_id.replace("SOC", "CPT")
        resultat.append(
            {
                "compte_id": compte_id,
                "date_operation": credit.date_deblocage,
                "type_operation": "transfert_nantie",
                "sens": "retrait",
                "montant": montant,
                "credit_id": credit.credit_id,
                "_ordre": ordre,
            }
        )
        ordre += 1
        if credit.statut == "solde":
            resultat.append(
                {
                    "compte_id": compte_id,
                    "date_operation": credit.date_issue,
                    "type_operation": "restitution_nantie",
                    "sens": "depot",
                    "montant": montant,
                    "credit_id": credit.credit_id,
                    "_ordre": ordre,
                }
            )
            ordre += 1
    dataframe = (
        pd.DataFrame(resultat)
        .sort_values(["compte_id", "date_operation", "_ordre"])
        .reset_index(drop=True)
    )
    # Un retrait libre demande apres le blocage ne peut consommer la nantie. Le SIG
    # enregistre donc seulement le montant librement disponible. Un transfert de
    # nantie, lui, doit rester integral : son montant a ete controle a l'octroi.
    comptes = dataframe["compte_id"].to_numpy()
    sens = dataframe["sens"].to_numpy()
    types = dataframe["type_operation"].to_numpy()
    montants = dataframe["montant"].to_numpy(dtype=np.int64, copy=True)
    compte_courant = None
    solde = 0
    for index in range(len(dataframe)):
        if comptes[index] != compte_courant:
            compte_courant = comptes[index]
            solde = 0
        if sens[index] == "depot":
            solde += int(montants[index])
            continue
        montant = int(montants[index])
        if types[index] == "retrait":
            montant = min(montant, solde)
            montants[index] = montant
        elif montant > solde:
            raise ValueError(f"Nantissement superieur au solde libre du compte {comptes[index]}")
        solde -= montant
    dataframe["montant"] = montants
    dataframe.insert(0, "mouvement_id", [f"MVT-{i:08d}" for i in range(len(dataframe))])
    return dataframe


def construire_soldes_mensuels(membres, mouvements, date_fin):
    fin = pd.Timestamp(date_fin)
    operations = mouvements.copy()
    operations["mois"] = operations["date_operation"].dt.to_period("M").dt.to_timestamp()
    operations["depot"] = np.where(operations["sens"] == "depot", operations["montant"], 0)
    operations["retrait"] = np.where(operations["sens"] == "retrait", operations["montant"], 0)
    agregats = operations.groupby(["compte_id", "mois"], sort=False).agg(
        total_depots=("depot", "sum"),
        total_retraits=("retrait", "sum"),
        nb_operations=("montant", "size"),
    )
    depots_reguliers = (
        operations[operations["type_operation"] == "depot"].groupby(["compte_id", "mois"]).size()
    )

    lignes = []
    comptes = []
    for membre in membres.itertuples():
        compte_id = membre.societaire_id.replace("SOC", "CPT")
        solde = 0
        lignes_compte = []
        for mois in pd.date_range(pd.Timestamp(membre.date_adhesion), fin, freq="MS"):
            cle = (compte_id, mois)
            if cle in agregats.index:
                ligne_agregee = agregats.loc[cle]
                depots = int(ligne_agregee.total_depots)
                retraits = int(ligne_agregee.total_retraits)
                nombre = int(ligne_agregee.nb_operations)
            else:
                depots = retraits = nombre = 0
            solde += depots - retraits
            if solde < 0:
                raise ValueError(f"Solde libre negatif pour {compte_id} en {mois:%Y-%m}")
            ligne = {
                "compte_id": compte_id,
                "societaire_id": membre.societaire_id,
                "type_compte": "epargne_libre",
                "mois": mois,
                "solde_fin_mois": solde,
                "total_depots": depots,
                "total_retraits": retraits,
                "nb_operations": nombre,
            }
            lignes.append(ligne)
            lignes_compte.append(ligne)

        soldes = np.array([ligne["solde_fin_mois"] for ligne in lignes_compte], dtype=float)
        moyenne_6m = float(soldes[-6:].mean()) if len(soldes) else 0.0
        douze_derniers = lignes_compte[-12:]
        nb_mois_depot = sum(
            (compte_id, ligne["mois"]) in depots_reguliers.index for ligne in douze_derniers
        )
        solde_depart = soldes[-12] if len(soldes) >= 12 else 0.0
        croissance = (
            (soldes[-1] - solde_depart) / max(abs(solde_depart), 1_000) if len(soldes) else 0.0
        )
        variations = np.diff(np.r_[0.0, soldes[-12:]]) if len(soldes) else np.array([0.0])
        volatilite = (
            float(np.std(variations) / max(np.mean(soldes[-12:]), 1.0)) if len(soldes) else 0.0
        )
        comptes.append(
            {
                "compte_id": compte_id,
                "societaire_id": membre.societaire_id,
                "type_compte": "epargne_libre",
                "date_ouverture": membre.date_adhesion,
                "solde_actuel": int(soldes[-1]) if len(soldes) else 0,
                "statut": "actif",
                "solde_epargne_moyen_6m": moyenne_6m,
                "nb_mois_avec_depot_12m": int(nb_mois_depot),
                "croissance_epargne_12m": float(croissance),
                "volatilite_epargne": volatilite,
            }
        )
    return pd.DataFrame(comptes), pd.DataFrame(lignes)


def injecter_manquants(cfg, rng, membres):
    resultat = membres.copy()
    probabilites = np.where(
        resultat["zone"].values == "rural",
        cfg["manquant_revenu_rural"],
        cfg["manquant_revenu_urbain"],
    )
    resultat.loc[rng.random(len(resultat)) < probabilites, "revenu_declare"] = np.nan
    resultat.loc[rng.random(len(resultat)) < cfg["manquant_education"], "niveau_education"] = None
    return resultat


def controles(cfg, donnees):
    fin = pd.Timestamp(cfg["date_fin"])
    credits = donnees["credits"]
    resolus = credits[credits["defaut"] >= 0]
    mouvements = donnees["mouvements_epargne"]
    mensuel = donnees["solde_mensuel_epargne"]
    dates_reelles = pd.to_datetime(donnees["echeances"]["date_paiement_reelle"].dropna())
    return {
        "taux_souffrance_resolus": round(float(resolus["defaut"].mean()), 4)
        if len(resolus)
        else 0.0,
        "part_credits_en_cours": round(float((credits["defaut"] < 0).mean()), 4)
        if len(credits)
        else 0.0,
        "part_membres_emprunteurs": round(
            credits["societaire_id"].nunique() / max(len(donnees["societaires"]), 1), 4
        ),
        "evenements_apres_date_fin": int(
            (mouvements["date_operation"] > fin).sum() + (dates_reelles > fin).sum()
        ),
        "soldes_libres_negatifs": int((mensuel["solde_fin_mois"] < 0).sum()),
        "anciennete_min_mois": int(donnees["societaires"]["anciennete_societaire_mois"].min()),
        "anciennete_max_mois": int(donnees["societaires"]["anciennete_societaire_mois"].max()),
        "n_membres": len(donnees["societaires"]),
        "n_credits": len(credits),
        "n_echeances": len(donnees["echeances"]),
    }


def generer_donnees(cfg=None):
    cfg = charger_config() if cfg is None else cfg
    rng = np.random.default_rng(cfg["graine"])
    membres = gen_membres(cfg, rng)
    mouvements_base, historiques, ordre = gen_epargne_base(cfg, rng, membres)
    membres, groupes, appartenances, qualite = gen_gie(cfg, rng, membres)
    choc = gen_choc(cfg, rng)
    credits, _ = gen_credits(cfg, rng, membres, choc, qualite, historiques)
    credits, echeances = gen_echeances(cfg, rng, credits)
    garanties = gen_garanties(credits, appartenances, rng)
    mouvements = ajouter_mouvements_nantissement(mouvements_base, credits, ordre)
    comptes, soldes_mensuels = construire_soldes_mensuels(membres, mouvements, cfg["date_fin"])
    membres = injecter_manquants(cfg, rng, membres)
    produits = gen_produits(cfg)
    return {
        "societaires": membres,
        "credits": credits,
        "groupes_gie": groupes,
        "appartenances_gie": appartenances,
        "comptes_epargne": comptes,
        "mouvements_epargne": mouvements.drop(columns=["_ordre"]),
        "solde_mensuel_epargne": soldes_mensuels,
        "echeances": echeances,
        "garanties": garanties,
        "produits_credit": produits,
        "choc_secteur": choc.to_frame("choc_sectoriel"),
    }


def ecrire_sorties(donnees, dossier=RACINE / "sorties"):
    dossier = Path(dossier)
    dossier.mkdir(exist_ok=True)

    def sans_latentes(dataframe):
        return dataframe[
            [colonne for colonne in dataframe.columns if not colonne.startswith("lat_")]
        ]

    for nom, dataframe in donnees.items():
        sans_latentes(dataframe).to_parquet(dossier / f"{nom}.parquet")
    donnees["credits"].to_parquet(dossier / "_credits_latents.parquet")
    donnees["societaires"].to_parquet(dossier / "_societaires_latents.parquet")


if __name__ == "__main__":
    configuration = charger_config()
    tables = generer_donnees(configuration)
    rapport = controles(configuration, tables)
    ecrire_sorties(tables)
    print("=== RAPPORT COHERENCE / DATES (decisions terrain J1-05 a J1-13) ===")
    for cle, valeur in rapport.items():
        print(f"  {cle:30s}: {valeur}")
