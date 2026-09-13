import copy
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

SIMULATEUR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIMULATEUR / "simulateur"))

import pipeline  # noqa: E402


class TestReglesDeterministes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = pipeline.charger_config()

    def test_repartition_anciennete_15_25_60_et_minimum_trois_mois(self):
        anciennetes = pipeline.tirer_anciennetes_mois(np.random.default_rng(42), 10_000, 14 * 12)
        self.assertEqual(3, int(anciennetes.min()))
        self.assertLessEqual(int(anciennetes.max()), 14 * 12)
        self.assertAlmostEqual(0.15, np.mean(anciennetes <= 5), delta=0.005)
        self.assertAlmostEqual(0.25, np.mean((anciennetes >= 6) & (anciennetes <= 11)), delta=0.005)
        self.assertAlmostEqual(0.60, np.mean(anciennetes >= 12), delta=0.005)

    def test_rupture_de_pente_exacte_a_33_pourcent(self):
        coef = 0.75
        seuil = 0.33
        self.assertAlmostEqual(0.15, pipeline.effet_endettement(0.20, seuil, coef))
        self.assertAlmostEqual(0.2475, pipeline.effet_endettement(seuil, seuil, coef))
        self.assertAlmostEqual(
            coef * seuil + 2 * coef * (0.50 - seuil),
            pipeline.effet_endettement(0.50, seuil, coef),
        )

    def test_catalogue_et_montants_synthetiques(self):
        produits = pipeline.gen_produits(self.cfg).set_index("segment")
        self.assertTrue((produits["montant_min"] == 0).all())
        self.assertTrue((produits["montant_max"] == 100_000_000).all())
        attendu = {
            "jeune": (0.07, 0.075),
            "individuel": (0.14, 0.14),
            "salarie": (0.09, 0.12),
            "femme_gie": (0.16, 0.16),
            "agricole": (0.14, 0.14),
        }
        for segment, bornes in attendu.items():
            self.assertEqual(
                bornes, tuple(produits.loc[segment, ["taux_annuel_min", "taux_annuel_max"]])
            )

        rng = np.random.default_rng(42)
        montants = [pipeline.tirer_montant_credit(self.cfg, rng, 10_000_000) for _ in range(2_000)]
        self.assertGreaterEqual(min(montants), 20_000)
        self.assertLessEqual(max(montants), 5_500_000)

    def test_periodicites_compatibles_avec_la_duree(self):
        self.assertEqual(["hebdomadaire", "mensuelle"], pipeline.periodicites_compatibles(5))
        self.assertIn("trimestrielle", pipeline.periodicites_compatibles(9))
        self.assertNotIn("semestrielle", pipeline.periodicites_compatibles(9))
        self.assertIn("annuelle", pipeline.periodicites_compatibles(24))
        self.assertIn("semestrielle", pipeline.periodicites_compatibles(24))

    def test_echeancier_total_charge_et_endettement(self):
        echeances, total, charge = pipeline.construire_echeancier_theorique(
            montant=1_000_000,
            taux_annuel=0.12,
            duree_mois=12,
            periodicite="mensuelle",
            date_deblocage=pd.Timestamp("2025-01-15"),
        )
        self.assertEqual(12, len(echeances))
        self.assertAlmostEqual(total, sum(e["montant_prevu"] for e in echeances), delta=1)
        self.assertAlmostEqual(total / 12, charge, places=8)
        self.assertAlmostEqual(charge / 250_000, pipeline.ratio_endettement(charge, 250_000))
        interets = [e["montant_interet"] for e in echeances]
        self.assertTrue(all(a >= b for a, b in zip(interets, interets[1:], strict=False)))


class TestPipelineIntegre(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg = copy.deepcopy(pipeline.charger_config())
        cfg["n_membres"] = 600
        cls.cfg = cfg
        cls.donnees = pipeline.generer_donnees(cfg)

    def test_trois_mois_avant_tout_credit(self):
        membres = self.donnees["societaires"].set_index("societaire_id")
        credits = self.donnees["credits"]
        delta = credits["date_deblocage"] - credits["societaire_id"].map(membres["date_adhesion"])
        self.assertTrue((delta >= pd.Timedelta(days=89)).all())

    def test_taux_periodicite_charge_et_ratio(self):
        credits = self.donnees["credits"]
        produits = self.donnees["produits_credit"].set_index("produit_id")
        revenus = self.donnees["societaires"].set_index("societaire_id")["revenu_declare"]
        for credit in credits.itertuples():
            produit = produits.loc[credit.produit_id]
            self.assertGreaterEqual(credit.taux_annuel, produit.taux_annuel_min)
            self.assertLessEqual(credit.taux_annuel, produit.taux_annuel_max)
            self.assertIn(
                credit.periodicite_remboursement,
                pipeline.periodicites_compatibles(credit.duree_mois),
            )
            revenu = revenus.loc[credit.societaire_id]
            if pd.notna(revenu):
                self.assertAlmostEqual(
                    credit.endettement, credit.charge_mensualisee / revenu, places=10
                )

    def test_echeances_et_retards_de_groupe(self):
        credits = self.donnees["credits"].set_index("credit_id")
        echeances = self.donnees["echeances"]
        totaux = echeances.groupby("credit_id")["montant_prevu"].sum()
        for credit_id, total in totaux.items():
            self.assertAlmostEqual(total, credits.loc[credit_id, "total_a_rembourser"], delta=1)
        groupe = credits[credits["segment"] == "femme_gie"]
        if len(groupe):
            niveaux = echeances[echeances["credit_id"].isin(groupe.index)]["niveau_enregistrement"]
            self.assertTrue((niveaux == "groupe").all())
            self.assertTrue(
                echeances[echeances["credit_id"].isin(groupe.index)]["societaire_id"].isna().all()
            )
        self.assertTrue((credits.loc[credits["defaut"] == 1, "jours_retard_max"] >= 30).all())
        self.assertTrue((credits.loc[credits["defaut"] == 0, "jours_retard_max"] < 30).all())
        observes = echeances["jours_retard"].notna()
        self.assertTrue(
            (
                echeances.loc[observes, "alerte_operationnelle"]
                == (echeances.loc[observes, "jours_retard"] >= 1)
            ).all()
        )

    def test_nantissement_et_transferts_equilibres(self):
        garanties = self.donnees["garanties"]
        credits = self.donnees["credits"].set_index("credit_id")
        nanties = garanties[garanties["type_garantie"] == "epargne_nantie"]
        for garantie in nanties.itertuples():
            montant = credits.loc[garantie.credit_id, "montant_octroye"]
            self.assertGreaterEqual(garantie.montant_garanti, 0.10 * montant - 1)
            self.assertLessEqual(garantie.montant_garanti, montant / 3 + 1)

        mouvements = self.donnees["mouvements_epargne"]
        transferts = mouvements[
            mouvements["type_operation"].isin(["transfert_nantie", "restitution_nantie"])
        ]
        soldes = (
            transferts.assign(
                signe=np.where(
                    transferts["sens"].eq("depot"), transferts["montant"], -transferts["montant"]
                )
            )
            .groupby("credit_id", dropna=True)["signe"]
            .sum()
        )
        credits_soldes = credits[credits["statut"] == "solde"].index
        self.assertTrue((soldes.reindex(credits_soldes, fill_value=0) == 0).all())

    def test_identite_mensuelle_soldes_non_negatifs_et_dates(self):
        mensuel = self.donnees["solde_mensuel_epargne"].sort_values(["compte_id", "mois"])
        precedent = mensuel.groupby("compte_id")["solde_fin_mois"].shift(fill_value=0)
        attendu = precedent + mensuel["total_depots"] - mensuel["total_retraits"]
        np.testing.assert_allclose(attendu, mensuel["solde_fin_mois"], atol=1)
        self.assertTrue((mensuel["solde_fin_mois"] >= 0).all())
        comptes = self.donnees["comptes_epargne"].set_index("compte_id")
        derniers = mensuel.groupby("compte_id").tail(1).set_index("compte_id")
        np.testing.assert_allclose(derniers["solde_fin_mois"], comptes["solde_actuel"], atol=1)

        fin = pd.Timestamp(self.cfg["date_fin"])
        colonnes_dates = {
            "societaires": ["date_adhesion"],
            "credits": ["date_deblocage"],
            "echeances": ["date_paiement_reelle"],
            "mouvements_epargne": ["date_operation"],
        }
        for table, colonnes in colonnes_dates.items():
            for colonne in colonnes:
                valeurs = pd.to_datetime(self.donnees[table][colonne].dropna())
                self.assertTrue((valeurs <= fin).all(), f"{table}.{colonne}")

    def test_age_absent_du_risque_et_reproductibilite(self):
        self.assertNotIn("age", pipeline.VARIABLES_RISQUE_OCTROI)
        cfg = copy.deepcopy(self.cfg)
        autres = pipeline.generer_donnees(cfg)
        pd.testing.assert_frame_equal(self.donnees["credits"], autres["credits"])
        pd.testing.assert_frame_equal(
            self.donnees["solde_mensuel_epargne"], autres["solde_mensuel_epargne"]
        )


if __name__ == "__main__":
    unittest.main()
