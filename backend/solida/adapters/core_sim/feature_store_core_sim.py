from datetime import date

from solida_modelisation.features_epargne import calculer_features_epargne
from solida_modelisation.features_groupe import calculer_features_groupe

from solida.domain.entities.credit import Credit
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.values.features import FeaturesIndividuelles, FeaturesSolidaires


def _mois_ecoules(debut: date, fin: date) -> int:
    """Calcule une ancienneté à la date de décision, jamais à l'instant présent."""
    valeur = (fin.year - debut.year) * 12 + fin.month - debut.month
    if fin.day < debut.day:
        valeur -= 1
    return max(valeur, 0)


def _nb_incidents_anterieurs(credits: list[Credit]) -> int:
    return sum(1 for c in credits if (c.jours_retard_max or 0) >= 30)


def _max_jours_retard(credits: list[Credit]) -> int | None:
    values = [credit.jours_retard_max for credit in credits if credit.jours_retard_max is not None]
    return max(values) if values else None


def _montant_max_rembourse(credits: list[Credit]) -> int | None:
    """Plus grand montant correctement remboursé, feature historique du SOCLE."""
    return max(
        (
            c.montant_octroye
            for c in credits
            if c.statut == "solde" and (c.jours_retard_max or 0) < 30
        ),
        default=None,
    )


class FeatureStoreCoreSim:
    """Calcule les features de profil à partir de CORE-SIM.

    Les ratios liés à une demande sont recalculés par `ScorerDemande` avant le scoring.
    """

    def __init__(self, core_sim_reader: CoreSimReader) -> None:
        self._core_sim_reader = core_sim_reader

    def lire_individuelles(
        self, societaire_id: str, date_reference: date
    ) -> FeaturesIndividuelles | None:
        societaire = self._core_sim_reader.charger_societaire(societaire_id)
        if societaire is None:
            return None

        credits = [
            credit
            for credit in self._core_sim_reader.charger_historique_credit(societaire_id)
            if credit.date_deblocage < date_reference
        ]
        soldes = self._core_sim_reader.charger_soldes_mensuels(societaire_id, date_reference)
        # Même fonction pure qu'à l'entraînement (`solida_modelisation.features_epargne`) :
        # la parité tient à l'identité du code, pas à une réimplémentation surveillée (J2-11).
        epargne = calculer_features_epargne(soldes, date_reference)
        solde_moyen_6m = round(epargne.solde_epargne_moyen_6m)

        revenu = societaire.revenu_mensuel_declare
        ratio_epargne_revenu = (
            min(solde_moyen_6m / revenu, 5.0) if revenu is not None and revenu > 0 else None
        )
        montant_max = _montant_max_rembourse(credits)

        return FeaturesIndividuelles(
            anciennete_societaire_mois=_mois_ecoules(societaire.date_adhesion, date_reference),
            segment=societaire.segment,
            solde_epargne_moyen_6m=solde_moyen_6m,
            nb_mois_avec_depot_12m=epargne.nb_mois_avec_depot_12m,
            tendance_epargne_12m=epargne.tendance_epargne_12m,
            volatilite_epargne=epargne.volatilite_epargne,
            ratio_epargne_revenu=ratio_epargne_revenu,
            ratio_epargne_montant=0.0,
            anciennete_epargne_mois=_mois_ecoules(societaire.date_adhesion, date_reference),
            ratio_endettement=None,
            nb_credits_anterieurs=len(credits),
            nb_incidents_anterieurs=_nb_incidents_anterieurs(credits),
            max_jours_retard_historique=_max_jours_retard(credits),
            montant_max_rembourse=montant_max,
            numero_cycle=len(credits) + 1,
            parts_sociales_montant=societaire.parts_sociales_montant,
            nb_personnes_a_charge=societaire.nb_personnes_a_charge,
            zone_residence=societaire.zone,
            revenu_mensuel_declare=revenu,
            ratio_montant_historique=None,
        )

    def lire_solidaires(self, gie_id: str, date_reference: date) -> FeaturesSolidaires | None:
        """Historique du groupe emprunteur lui-même — jamais celui d'un tiers du groupe
        (arbitrage 2026-09-14). `calculer_features_groupe` est la même fonction pure que
        celle utilisée à l'entraînement (`solida_modelisation.features_groupe`) : la
        parité tient à l'identité du code, pas à une réimplémentation surveillée."""
        donnees = self._core_sim_reader.charger_donnees_groupe(gie_id)
        if donnees is None:
            return None

        resultat = calculer_features_groupe(
            date_reference=date_reference,
            date_creation_groupe=donnees.date_creation,
            appartenances=donnees.appartenances,
            credits_anterieurs=donnees.credits_anterieurs,
            echeances_groupe=donnees.echeances_groupe,
            cautions_anterieures=donnees.cautions_anterieures,
        )
        return FeaturesSolidaires(
            taille_groupe=resultat.taille_groupe,
            anciennete_groupe_mois=resultat.anciennete_groupe_mois,
            nb_credits_groupe_anterieurs=resultat.nb_credits_groupe_anterieurs,
            nb_incidents_groupe_anterieurs=resultat.nb_incidents_groupe_anterieurs,
            max_jours_retard_groupe_6m=resultat.max_jours_retard_groupe_6m,
            nb_cautions_appelees_anterieures=resultat.nb_cautions_appelees_anterieures,
        )

    def date_dernier_rafraichissement(self, societaire_id: str) -> date | None:
        return date.today()
