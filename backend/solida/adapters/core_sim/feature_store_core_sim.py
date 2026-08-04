from datetime import date

from solida.domain.entities.credit import Credit
from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.rules.echeance import TAUX_MENSUEL_DEMONSTRATION, calculer_echeance_mensuelle
from solida.domain.rules.epargne import tendance_depuis_croissance
from solida.domain.values.features import FeaturesIndividuelles, FeaturesSolidaires


def _nb_incidents_anterieurs(credits: list[Credit]) -> int:
    return sum(1 for c in credits if c.statut == "en_souffrance")


def _max_jours_retard(credits: list[Credit]) -> int | None:
    valeurs = [c.jours_retard_max for c in credits if c.jours_retard_max is not None]
    return max(valeurs) if valeurs else None


def _montant_max_rembourse(credits: list[Credit]) -> int | None:
    """Base historique de la progression : le plus gros montant déjà accordé, quel
    qu'en soit le statut final — le risque du profil est déjà pris en compte
    séparément par la modulation de `calculer_plafond` sur la probabilité de défaut.
    """
    return max((c.montant_octroye for c in credits), default=None)


class FeatureStoreCoreSim:
    """Calcule les features à la demande à partir de CORE-SIM — pas de feature store
    historisé pour cette passe (voir `docs/backend/03-decisions-provisoires-a-revoir.md`).

    `ratio_endettement`, `ratio_epargne_montant` et `ratio_epargne_revenu` dépendent du
    montant et de la durée d'une demande précise, que ce port ne connaît pas (il ne prend
    que `societaire_id`). Les valeurs renvoyées ici sont un instantané de profil basé sur
    le dernier crédit connu ; `scorer_demande` les recalcule et les remplace toujours avec
    les chiffres réels de la demande avant de construire les features envoyées au modèle
    et avant persistance — ce qui compte pour l'audit et pour le modèle réel à venir.
    """

    def __init__(self, lecteur: LecteurCoreSim) -> None:
        self._lecteur = lecteur

    def lire_individuelles(self, societaire_id: str) -> FeaturesIndividuelles | None:
        societaire = self._lecteur.charger_societaire(societaire_id)
        if societaire is None:
            return None

        credits = self._lecteur.charger_historique_credit(societaire_id)
        compte = self._lecteur.charger_compte_epargne(societaire_id)

        solde_moyen_6m = compte.solde_moyen_6m if compte else 0
        nb_mois_avec_depot_12m = compte.nb_mois_avec_depot_12m if compte else 0
        volatilite = compte.volatilite if compte else 0.0
        tendance = tendance_depuis_croissance(compte.croissance_12m if compte else 0.0)

        revenu = societaire.revenu_mensuel_declare or 0
        dernier_credit = credits[0] if credits else None
        montant_reference = dernier_credit.montant_octroye if dernier_credit else 0
        echeance_reference = (
            calculer_echeance_mensuelle(
                montant_reference, dernier_credit.duree_mois, TAUX_MENSUEL_DEMONSTRATION
            )
            if dernier_credit
            else 0
        )
        ratio_endettement = (echeance_reference / revenu) if revenu > 0 else 0.0
        ratio_epargne_montant = (
            min(solde_moyen_6m / montant_reference, 3.0) if montant_reference > 0 else 0.0
        )
        ratio_epargne_revenu = min(solde_moyen_6m / revenu, 5.0) if revenu > 0 else 0.0

        return FeaturesIndividuelles(
            anciennete_societaire_mois=societaire.anciennete_mois,
            segment=societaire.segment,
            solde_epargne_moyen_6m=solde_moyen_6m,
            nb_mois_avec_depot_12m=nb_mois_avec_depot_12m,
            tendance_epargne_12m=tendance,
            volatilite_epargne=volatilite,
            ratio_epargne_revenu=ratio_epargne_revenu,
            ratio_epargne_montant=ratio_epargne_montant,
            anciennete_epargne_mois=societaire.anciennete_mois,
            ratio_endettement=ratio_endettement,
            nb_credits_anterieurs=len(credits),
            nb_incidents_anterieurs=_nb_incidents_anterieurs(credits),
            max_jours_retard_historique=_max_jours_retard(credits),
            montant_max_rembourse=_montant_max_rembourse(credits),
            numero_cycle=len(credits) + 1,
            parts_sociales_montant=societaire.parts_sociales_montant,
            nb_personnes_a_charge=societaire.nb_personnes_a_charge,
        )

    def lire_solidaires(self, societaire_id: str) -> FeaturesSolidaires | None:
        groupe = self._lecteur.charger_groupe(societaire_id)
        if groupe is None:
            return FeaturesSolidaires(
                en_groupe=False,
                groupe_id=None,
                taille_groupe=None,
                taux_remboursement_groupe=None,
                deja_secouru_par_groupe=None,
            )

        garanties = self._lecteur.charger_garanties(societaire_id)
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
