import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from solida.application.use_cases.scorer_demande_features import (
    _actualiser_features,
    _features_to_dict,
    _revenu_effectif,
)
from solida.application.use_cases.scorer_demande_validations import (
    PLAFOND_INSTITUTIONNEL_FCFA,
    valider_acces_agence,
    valider_duree_dans_bornes,
    valider_montant_sous_plafond_institutionnel,
    valider_pas_de_credit_en_cours,
    valider_pas_de_multi_octroi,
    valider_produit_catalogue,
    valider_societaire_trouve,
)
from solida.domain.errors import DonneesInsuffisantes
from solida.domain.ports.audit import AuditLog
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.decisions import DecisionRepository
from solida.domain.ports.feature_store import FeatureStore
from solida.domain.ports.grille import GrilleRepository
from solida.domain.ports.modele import ScoringModel
from solida.domain.rules.grille import decider
from solida.domain.rules.progressif_reexamen import (
    ParametresReexamen,
    SituationReexamen,
    lister_conditions_reexamen,
)
from solida.domain.rules.scorecard import (
    calculer_score,
    decomposer_en_points,
    verifier_invariant_decomposition,
)
from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree
from solida.domain.values.demande import DemandeScoring
from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.montant import Montant

AVERTISSEMENT_MODELE_SYNTHESE = (
    "Modèle entraîné sur données synthétiques : recommandation de démonstration à recalibrer "
    "sur l'historique de la coopérative avant tout usage réel."
)
AVERTISSEMENT_REVENU_MANQUANT = (
    "Le revenu mensuel est absent : les ratios associés ont été traités comme informations "
    "manquantes par le modèle."
)

# Alignée sur la durée de session pour bloquer un multi-octroi avant le reflet CORE-SIM.
FENETRE_MULTI_OCTROI = timedelta(hours=8)


@dataclass(frozen=True)
class ScorerDemande:
    core_sim_reader: CoreSimReader
    feature_store: FeatureStore
    scoring_model: ScoringModel
    grille_repository: GrilleRepository
    decision_repository: DecisionRepository
    audit_log: AuditLog

    def preview(
        self,
        demande: DemandeScoring,
        raw_input: dict[str, object],
        agent_id: str,
        agent_nom: str,
        agent_agence_id: str | None,
    ) -> DecisionAEnregistrer:
        """Calcule le score sans l'enregistrer — l'agent doit encore confirm avant que
        quoi que ce soit ne soit écrit dans le registre des décisions."""
        decision = self._calculate(demande, raw_input, agent_id, agent_nom, agent_agence_id)
        self.audit_log.enregistrer_evenement(
            "scoring_previsualise", agent_id, demande.societaire_id, {}
        )
        return decision

    def confirm(
        self,
        demande: DemandeScoring,
        raw_input: dict[str, object],
        agent_id: str,
        agent_nom: str,
        agent_agence_id: str | None,
    ) -> DecisionEnregistree:
        """Recalcule à l'identique (les features CORE-SIM peuvent avoir changé entre la
        prévisualisation et la confirmation — limite documentée, acceptable pour cette
        passe) puis persiste, cette fois pour de bon."""
        decision = self._calculate(demande, raw_input, agent_id, agent_nom, agent_agence_id)
        enregistree = self.decision_repository.enregistrer(decision)
        self.audit_log.enregistrer_evenement(
            "scoring_confirme", agent_id, demande.societaire_id, {}
        )
        return enregistree

    def _calculate(
        self,
        demande: DemandeScoring,
        raw_input: dict[str, object],
        agent_id: str,
        agent_nom: str,
        agent_agence_id: str | None,
    ) -> DecisionAEnregistrer:
        societaire = valider_societaire_trouve(
            self.core_sim_reader.charger_societaire(demande.societaire_id), demande.societaire_id
        )
        valider_acces_agence(societaire, agent_agence_id)
        valider_pas_de_credit_en_cours(societaire, demande.societaire_id)
        since = datetime.now(UTC) - FENETRE_MULTI_OCTROI
        valider_pas_de_multi_octroi(
            self.decision_repository, demande.societaire_id, since, raw_input
        )

        configuration = self.grille_repository.lire_active()
        valider_montant_sous_plafond_institutionnel(demande.montant_demande)
        catalogue_produit = valider_produit_catalogue(
            self.core_sim_reader.charger_produits(), demande.produit_id
        )
        valider_duree_dans_bornes(demande.duree_demandee_mois, catalogue_produit)

        features_individuelles = self.feature_store.lire_individuelles(
            demande.societaire_id, datetime.now(UTC).date()
        )
        if features_individuelles is None:
            raise DonneesInsuffisantes(
                f"Les données de {demande.societaire_id} ne permettent pas de calculer un score."
            )

        revenu_effectif = _revenu_effectif(demande, societaire.revenu_mensuel_declare)
        features_actualisees = _actualiser_features(
            features_individuelles, demande, revenu_effectif, catalogue_produit.taux_annuel
        )

        features_dict = _features_to_dict(features_actualisees, demande)
        probabilite = self.scoring_model.predire(features_dict)
        contributions_log_odds = self.scoring_model.contributions(features_dict)

        score = calculer_score(probabilite, configuration.scorecard)
        beta_0 = math.log((1 - probabilite.valeur) / probabilite.valeur) - sum(
            v for _, v in contributions_log_odds
        )
        points_de_base, points = decomposer_en_points(
            beta_0, contributions_log_odds, configuration.scorecard
        )
        verifier_invariant_decomposition(points_de_base, points, score)

        tranche = decider(probabilite, configuration.grille)

        montant_demande_v = Montant(valeur=demande.montant_demande)
        plafond_institutionnel = Montant(valeur=PLAFOND_INSTITUTIONNEL_FCFA)

        situation = SituationReexamen(
            regularite_epargne=features_actualisees.nb_mois_avec_depot_12m / 12,
            ratio_garantie=features_actualisees.ratio_epargne_montant,
            endettement=features_actualisees.ratio_endettement,
            tendance_epargne_baissiere=features_actualisees.tendance_epargne_12m == "erosion",
            # La caution solidaire est une information du modèle enrichi, pas du SOCLE.
            caution_deja_appelee=False,
            montant_demande=montant_demande_v,
        )
        conditions = lister_conditions_reexamen(situation, ParametresReexamen())

        return DecisionAEnregistrer(
            decision_id=str(uuid.uuid4()),
            agent_id=agent_id,
            agent_nom=agent_nom,
            agent_agence_id=agent_agence_id,
            societaire_id=demande.societaire_id,
            entree=raw_input,
            features_utilisees=features_dict,
            probabilite=probabilite.valeur,
            score=score,
            tranche=tranche,
            montant_recommande=montant_demande_v,
            mode_calcul=ModeCalcul.SOCLE_SEUL,
            motif_mode=None,
            points_de_base=points_de_base,
            decomposition=points,
            # Contrat conservé : le champ historique ne porte plus une progression.
            plafond_progressif=plafond_institutionnel,
            trajectoire_progression=[],
            conditions_reexamen=conditions,
            avertissements=[
                AVERTISSEMENT_MODELE_SYNTHESE,
                *([AVERTISSEMENT_REVENU_MANQUANT] if revenu_effectif is None else []),
            ],
            version_modele=self.scoring_model.version(),
            version_grille=configuration.version_grille,
        )
