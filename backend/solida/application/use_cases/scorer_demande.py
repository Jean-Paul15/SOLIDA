import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from solida.application.use_cases.scorer_demande_features import (
    _actualiser_features,
    _features_vers_dict,
    _revenu_effectif,
)
from solida.application.use_cases.scorer_demande_validations import (
    valider_acces_agence,
    valider_duree_dans_bornes,
    valider_montant_sous_plafond,
    valider_pas_de_credit_en_cours,
    valider_pas_de_multi_octroi,
    valider_plafond_produit,
    valider_produit_catalogue,
    valider_societaire_trouve,
)
from solida.domain.erreurs import DonneesInsuffisantes
from solida.domain.ports.audit import AuditLog
from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.ports.decisions import DecisionRepository
from solida.domain.ports.feature_store import FeatureStore
from solida.domain.ports.grille import GrilleRepository
from solida.domain.ports.modele import ScoringModel
from solida.domain.rules.cascade import ContexteCascade, ParametresCascade, determiner_mode
from solida.domain.rules.grille import decider
from solida.domain.rules.progressif_plafond import calculer_plafond
from solida.domain.rules.progressif_reexamen import (
    ParametresReexamen,
    SituationReexamen,
    lister_conditions_reexamen,
)
from solida.domain.rules.progressif_trajectoire import calculer_trajectoire
from solida.domain.rules.scorecard import (
    calculer_score,
    decomposer_en_points,
    verifier_invariant_decomposition,
)
from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree
from solida.domain.values.demande import DemandeScoring
from solida.domain.values.montant import Montant

AVERTISSEMENT_MODELE_SUBSTITUT = (
    "Score calculé avec un modèle de substitution (probabilité fixe), pas le modèle "
    "réel entraîné : à recalibrer entièrement dès qu'il existe."
)

# Reprend la duree de session deja actee (DUREE_SESSION_SECONDES, infrastructure/auth.py — pas
# importable ici, l'application ne depend pas de l'infrastructure) plutot que d'inventer un
# nouveau seuil : au-dela d'une session de guichet, CORE-SIM a normalement eu le temps de
# refleter un octroi confirme ; en-deca, deux "accord" pour le meme societaire sont un signal de
# multi-octroi que le controle a_credit_en_cours seul ne voit pas encore.
FENETRE_MULTI_OCTROI = timedelta(hours=8)


@dataclass(frozen=True)
class ScorerDemande:
    lecteur: LecteurCoreSim
    feature_store: FeatureStore
    scoring_model: ScoringModel
    grille_repository: GrilleRepository
    decision_repository: DecisionRepository
    audit_log: AuditLog

    def previsualiser(
        self,
        demande: DemandeScoring,
        entree_brute: dict[str, object],
        agent_id: str,
        agent_nom: str,
        agent_agence_id: str | None,
    ) -> DecisionAEnregistrer:
        """Calcule le score sans l'enregistrer — l'agent doit encore confirmer avant que
        quoi que ce soit ne soit écrit dans le registre des décisions."""
        decision = self._calculer(demande, entree_brute, agent_id, agent_nom, agent_agence_id)
        self.audit_log.enregistrer_evenement(
            "scoring_previsualise", agent_id, demande.societaire_id, {}
        )
        return decision

    def confirmer(
        self,
        demande: DemandeScoring,
        entree_brute: dict[str, object],
        agent_id: str,
        agent_nom: str,
        agent_agence_id: str | None,
    ) -> DecisionEnregistree:
        """Recalcule à l'identique (les features CORE-SIM peuvent avoir changé entre la
        prévisualisation et la confirmation — limite documentée, acceptable pour cette
        passe) puis persiste, cette fois pour de bon."""
        decision = self._calculer(demande, entree_brute, agent_id, agent_nom, agent_agence_id)
        enregistree = self.decision_repository.enregistrer(decision)
        self.audit_log.enregistrer_evenement(
            "scoring_confirme", agent_id, demande.societaire_id, {}
        )
        return enregistree

    def _calculer(
        self,
        demande: DemandeScoring,
        entree_brute: dict[str, object],
        agent_id: str,
        agent_nom: str,
        agent_agence_id: str | None,
    ) -> DecisionAEnregistrer:
        societaire = valider_societaire_trouve(
            self.lecteur.charger_societaire(demande.societaire_id), demande.societaire_id
        )
        valider_acces_agence(societaire, agent_agence_id)
        valider_pas_de_credit_en_cours(societaire, demande.societaire_id)
        depuis = datetime.now(UTC) - FENETRE_MULTI_OCTROI
        valider_pas_de_multi_octroi(
            self.decision_repository, demande.societaire_id, depuis, entree_brute
        )

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
        probabilite = self.scoring_model.predire(features_dict)
        contributions_log_odds = self.scoring_model.contributions(features_dict)

        configuration = self.grille_repository.lire_active()
        plafond_produit_montant = valider_plafond_produit(
            configuration.progressif.plafonds_produits, demande.produit_id
        )
        valider_montant_sous_plafond(demande.montant_demande, plafond_produit_montant)
        catalogue_produit = valider_produit_catalogue(
            self.lecteur.charger_produits(), demande.produit_id
        )
        valider_duree_dans_bornes(demande.duree_demandee_mois, catalogue_produit)

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
            montant_max_rembourse,
            montant_demande_v,
            probabilite,
            configuration.progressif,
            plafond_produit_montant,
        )
        trajectoire = calculer_trajectoire(
            plafond, probabilite, configuration.progressif, plafond_produit_montant
        )

        situation = SituationReexamen(
            regularite_epargne=features_actualisees.nb_mois_avec_depot_12m / 12,
            ratio_garantie=features_actualisees.ratio_epargne_montant,
            endettement=features_actualisees.ratio_endettement,
            tendance_epargne_baissiere=features_actualisees.tendance_epargne_12m == "erosion",
            caution_deja_appelee=bool(features_solidaires.deja_secouru_par_groupe),
            montant_demande=montant_demande_v,
        )
        conditions = lister_conditions_reexamen(situation, ParametresReexamen())

        return DecisionAEnregistrer(
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
            version_modele=self.scoring_model.version(),
            version_grille=configuration.version_grille,
        )
