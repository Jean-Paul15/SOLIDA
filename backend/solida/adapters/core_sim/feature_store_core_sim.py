from datetime import date

from solida.domain.entities.credit import Credit
from solida.domain.entities.mouvement_epargne import MouvementEpargne
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.rules.epargne import tendance_depuis_croissance
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


def _premier_jour_mois(valeur: date) -> date:
    return valeur.replace(day=1)


def _mois_suivant(valeur: date) -> date:
    return date(valeur.year + (valeur.month == 12), (valeur.month % 12) + 1, 1)


def _statistiques_epargne_a_reference(
    mouvements: list[MouvementEpargne], date_ouverture: date, date_reference: date
) -> tuple[int, int, str, float]:
    """Rejoue les mois entièrement clos, en excluant le mois courant de la demande.

    CORE-SIM expose les mouvements datés et non un instantané mensuel historisé. Le
    calcul reproduit donc les quatre agrégats du dataset SOCLE à la date demandée.
    """
    limite = _premier_jour_mois(date_reference)
    par_mois: dict[date, list[MouvementEpargne]] = {}
    for mouvement in mouvements:
        if date_ouverture <= mouvement.date_operation < limite:
            par_mois.setdefault(_premier_jour_mois(mouvement.date_operation), []).append(mouvement)

    premier_mois = _premier_jour_mois(date_ouverture)
    premier_mois_complet = premier_mois if date_ouverture.day == 1 else _mois_suivant(premier_mois)
    mois = premier_mois
    solde = 0
    soldes_clotures: list[int] = []
    depots_reguliers: list[bool] = []
    while mois < limite:
        operations = par_mois.get(mois, [])
        solde += sum(mouvement.montant for mouvement in operations if mouvement.sens == "depot")
        solde -= sum(mouvement.montant for mouvement in operations if mouvement.sens == "retrait")
        if mois >= premier_mois_complet:
            soldes_clotures.append(solde)
            depots_reguliers.append(
                any(
                    mouvement.sens == "depot" and mouvement.type_operation == "depot"
                    for mouvement in operations
                )
            )
        mois = _mois_suivant(mois)

    six_derniers = soldes_clotures[-6:]
    douze_derniers = soldes_clotures[-12:]
    solde_moyen_6m = round(sum(six_derniers) / len(six_derniers)) if six_derniers else 0
    nb_mois_avec_depot_12m = sum(depots_reguliers[-12:])
    solde_depart = douze_derniers[0] if len(douze_derniers) >= 12 else 0
    solde_final = douze_derniers[-1] if douze_derniers else 0
    croissance = (solde_final - solde_depart) / max(abs(solde_depart), 1_000)
    variations = [
        valeur - precedent
        for precedent, valeur in zip([0, *douze_derniers], douze_derniers, strict=False)
    ]
    if not douze_derniers:
        volatilite = 0.0
    else:
        moyenne = sum(douze_derniers) / len(douze_derniers)
        moyenne_variations = sum(variations) / len(variations)
        ecart_type = (
            sum((variation - moyenne_variations) ** 2 for variation in variations) / len(variations)
        ) ** 0.5
        volatilite = ecart_type / max(moyenne, 1.0)
    return (
        solde_moyen_6m,
        nb_mois_avec_depot_12m,
        tendance_depuis_croissance(croissance),
        volatilite,
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
        mouvements = self._core_sim_reader.charger_mouvements_epargne(
            societaire_id, societaire.date_adhesion
        )
        (
            solde_moyen_6m,
            nb_mois_avec_depot_12m,
            tendance,
            volatilite,
        ) = _statistiques_epargne_a_reference(
            mouvements, societaire.date_adhesion, date_reference
        )

        revenu = societaire.revenu_mensuel_declare
        ratio_epargne_revenu = (
            min(solde_moyen_6m / revenu, 5.0) if revenu is not None and revenu > 0 else None
        )
        montant_max = _montant_max_rembourse(credits)

        return FeaturesIndividuelles(
            anciennete_societaire_mois=_mois_ecoules(societaire.date_adhesion, date_reference),
            segment=societaire.segment,
            solde_epargne_moyen_6m=solde_moyen_6m,
            nb_mois_avec_depot_12m=nb_mois_avec_depot_12m,
            tendance_epargne_12m=tendance,
            volatilite_epargne=volatilite,
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

    def lire_solidaires(self, societaire_id: str) -> FeaturesSolidaires | None:
        groupe = self._core_sim_reader.charger_groupe(societaire_id)
        if groupe is None:
            return FeaturesSolidaires(
                en_groupe=False,
                groupe_id=None,
                taille_groupe=None,
                taux_remboursement_groupe=None,
                deja_secouru_par_groupe=None,
            )

        garanties = self._core_sim_reader.charger_garanties(societaire_id)
        deja_secouru = any(
            g.beneficiaire_societaire_id == societaire_id and g.garantie_appelee for g in garanties
        )
        return FeaturesSolidaires(
            en_groupe=True,
            groupe_id=groupe.groupe_id,
            taille_groupe=groupe.taille_actuelle,
            taux_remboursement_groupe=groupe.taux_remboursement_groupe,
            deja_secouru_par_groupe=deja_secouru,
        )

    def date_dernier_rafraichissement(self, societaire_id: str) -> date | None:
        return date.today()
