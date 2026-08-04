import math
import uuid
from dataclasses import dataclass, replace

from solida.domain.erreurs import AccesRefuse, DonneesInsuffisantes, SocietaireIntrouvable
from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.ports.decisions import DepotDecisions
from solida.domain.ports.feature_store import FeatureStore
from solida.domain.ports.grille import DepotGrille
from solida.domain.ports.modele import ModeleScoring
from solida.domain.rules.cascade import ContexteCascade, ParametresCascade, determiner_mode
from solida.domain.rules.echeance import (
    TAUX_MENSUEL_DEMONSTRATION,
    calculer_echeance_mensuelle,
    calculer_taux_endettement,
)
from solida.domain.rules.grille import decider
from solida.domain.rules.progressif import (
    ParametresReexamen,
    SituationReexamen,
    calculer_plafond,
    calculer_trajectoire,
    lister_conditions_reexamen,
)
from solida.domain.rules.scorecard import (
    calculer_score,
    decomposer_en_points,
    verifier_invariant_decomposition,
)
from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree
from solida.domain.values.demande import DemandeScoring
from solida.domain.values.features import FeaturesIndividuelles
from solida.domain.values.montant import Montant

AVERTISSEMENT_MODELE_SUBSTITUT = (
    "Score calculé avec un modèle de substitution (probabilité fixe), pas le modèle "
    "réel entraîné : à recalibrer entièrement dès qu'il existe."
)


def _revenu_effectif(demande: DemandeScoring, revenu_declare: int | None) -> int:
    if demande.actualisation and demande.actualisation.revenu_mensuel_declare is not None:
        return demande.actualisation.revenu_mensuel_declare
    return revenu_declare or 0


def _actualiser_features(
    features: FeaturesIndividuelles, demande: DemandeScoring, revenu_effectif: int
) -> FeaturesIndividuelles:
    """Remplace les ratios qui dépendent du montant/de la durée demandés, ou d'un revenu
    actualisé par l'agent : `FeatureStore` ne connaît que le profil du sociétaire, pas la
    demande en cours (voir `FeatureStoreCoreSim`).
    """
    charges = demande.actualisation.charges_mensuelles if demande.actualisation else None
    mensualite = calculer_echeance_mensuelle(
        demande.montant_demande, demande.duree_demandee_mois, TAUX_MENSUEL_DEMONSTRATION
    )
    ratio_endettement = calculer_taux_endettement(charges or 0, revenu_effectif, mensualite)
    ratio_epargne_montant = min(features.solde_epargne_moyen_6m / demande.montant_demande, 3.0)
    ratio_epargne_revenu = (
        min(features.solde_epargne_moyen_6m / revenu_effectif, 5.0) if revenu_effectif > 0 else 0.0
    )
    nb_personnes_a_charge = (
        demande.actualisation.nb_personnes_a_charge
        if demande.actualisation and demande.actualisation.nb_personnes_a_charge is not None
        else features.nb_personnes_a_charge
    )
    return replace(
        features,
        ratio_endettement=ratio_endettement,
        ratio_epargne_montant=ratio_epargne_montant,
        ratio_epargne_revenu=ratio_epargne_revenu,
        nb_personnes_a_charge=nb_personnes_a_charge,
    )


def _features_vers_dict(individuelles: FeaturesIndividuelles, en_groupe: bool) -> dict[str, float]:
    """Ne garde que les champs numériques : `predire()`/`contributions()` attendent des
    variables du modèle, pas les champs texte (`segment`, `tendance_epargne_12m`), et une
    valeur `None` (primo-emprunteur) est omise plutôt que remplacée par un zéro trompeur.
    """
    valeurs: dict[str, float | None] = {
        "anciennete_societaire_mois": individuelles.anciennete_societaire_mois,
        "solde_epargne_moyen_6m": individuelles.solde_epargne_moyen_6m,
        "nb_mois_avec_depot_12m": individuelles.nb_mois_avec_depot_12m,
        "volatilite_epargne": individuelles.volatilite_epargne,
        "ratio_epargne_revenu": individuelles.ratio_epargne_revenu,
        "ratio_epargne_montant": individuelles.ratio_epargne_montant,
        "anciennete_epargne_mois": individuelles.anciennete_epargne_mois,
        "ratio_endettement": individuelles.ratio_endettement,
        "nb_credits_anterieurs": individuelles.nb_credits_anterieurs,
        "nb_incidents_anterieurs": individuelles.nb_incidents_anterieurs,
        "max_jours_retard_historique": individuelles.max_jours_retard_historique,
        "montant_max_rembourse": individuelles.montant_max_rembourse,
        "numero_cycle": individuelles.numero_cycle,
        "parts_sociales_montant": individuelles.parts_sociales_montant,
        "nb_personnes_a_charge": individuelles.nb_personnes_a_charge,
        "en_groupe": 1.0 if en_groupe else 0.0,
    }
    return {code: valeur for code, valeur in valeurs.items() if valeur is not None}


@dataclass(frozen=True)
class ScorerDemande:
    lecteur: LecteurCoreSim
    feature_store: FeatureStore
    modele: ModeleScoring
    depot_grille: DepotGrille
    depot_decisions: DepotDecisions

    def executer(
        self,
        demande: DemandeScoring,
        entree_brute: dict[str, object],
        agent_id: str,
        agent_nom: str,
        agent_agence_id: str | None,
    ) -> DecisionEnregistree:
        societaire = self.lecteur.charger_societaire(demande.societaire_id)
        if societaire is None:
            raise SocietaireIntrouvable(
                f"Aucun sociétaire ne correspond à l'identifiant {demande.societaire_id}."
            )
        if agent_agence_id is not None and societaire.agence != agent_agence_id:
            raise AccesRefuse("Ce sociétaire n'appartient pas à votre agence.")

        groupe = self.lecteur.charger_groupe(demande.societaire_id)
        features_individuelles = self.feature_store.lire_individuelles(demande.societaire_id)
        features_solidaires = self.feature_store.lire_solidaires(demande.societaire_id)
        if features_individuelles is None or features_solidaires is None:
            raise DonneesInsuffisantes(
                f"Les données de {demande.societaire_id} ne permettent pas de calculer un score."
            )

        revenu_effectif = _revenu_effectif(demande, societaire.revenu_mensuel_declare)
        features_actualisees = _actualiser_features(
            features_individuelles, demande, revenu_effectif
        )

        contexte_cascade = ContexteCascade(
            appartient_a_un_groupe=groupe is not None,
            taille_groupe=groupe.taille_actuelle if groupe else 0,
            nb_credits_anterieurs_groupe_soldes=(
                groupe.nb_credits_anterieurs_soldes if groupe else 0
            ),
            fraicheur_features_jours=0,
        )
        resultat_cascade = determiner_mode(contexte_cascade, ParametresCascade())

        features_dict = _features_vers_dict(features_actualisees, features_solidaires.en_groupe)
        probabilite = self.modele.predire(features_dict)
        contributions_log_odds = self.modele.contributions(features_dict)

        configuration = self.depot_grille.lire_active()
        score = calculer_score(probabilite, configuration.scorecard)
        beta_0 = math.log((1 - probabilite.valeur) / probabilite.valeur) - sum(
            v for _, v in contributions_log_odds
        )
        points_de_base, points = decomposer_en_points(
            beta_0, contributions_log_odds, configuration.scorecard
        )
        verifier_invariant_decomposition(points_de_base, points, score)

        tranche = decider(probabilite, configuration.grille)

        montant_max_rembourse = (
            Montant(valeur=features_actualisees.montant_max_rembourse)
            if features_actualisees.montant_max_rembourse is not None
            else None
        )
        montant_demande_v = Montant(valeur=demande.montant_demande)
        plafond = calculer_plafond(
            montant_max_rembourse, montant_demande_v, probabilite, configuration.progressif
        )
        trajectoire = calculer_trajectoire(plafond, configuration.progressif)

        situation = SituationReexamen(
            regularite_epargne=features_actualisees.nb_mois_avec_depot_12m / 12,
            ratio_garantie=features_actualisees.ratio_epargne_montant,
            endettement=features_actualisees.ratio_endettement,
            tendance_epargne_baissiere=features_actualisees.tendance_epargne_12m == "erosion",
            caution_deja_appelee=bool(features_solidaires.deja_secouru_par_groupe),
            montant_demande=montant_demande_v,
        )
        conditions = lister_conditions_reexamen(situation, ParametresReexamen())

        decision = DecisionAEnregistrer(
            decision_id=str(uuid.uuid4()),
            agent_id=agent_id,
            agent_nom=agent_nom,
            agent_agence_id=agent_agence_id,
            societaire_id=demande.societaire_id,
            entree=entree_brute,
            features_utilisees=features_dict,
            probabilite=probabilite.valeur,
            score=score,
            tranche=tranche,
            montant_recommande=plafond,
            mode_calcul=resultat_cascade.mode,
            motif_mode=resultat_cascade.motif,
            points_de_base=points_de_base,
            decomposition=points,
            plafond_progressif=plafond,
            trajectoire_progression=trajectoire,
            conditions_reexamen=conditions,
            avertissements=[AVERTISSEMENT_MODELE_SUBSTITUT],
            version_modele=self.modele.version(),
            version_grille=configuration.version_grille,
        )
        return self.depot_decisions.enregistrer(decision)
