import math
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from solida_modelisation.features_groupe import taille_groupe_a_date

from solida.application.use_cases.scorer_demande_features import (
    _actualiser_features,
    _features_to_dict,
    _features_to_dict_enrichi,
    _revenu_effectif,
)
from solida.application.use_cases.scorer_demande_validations import (
    valider_acces_agence,
    valider_duree_dans_bornes,
    valider_montant_sous_plafond_institutionnel,
    valider_pas_de_credit_en_cours,
    valider_pas_de_multi_octroi,
    valider_produit_catalogue,
    valider_societaire_trouve,
)
from solida.domain.errors import DonneesInsuffisantes, ModeleIndisponible
from solida.domain.ports.audit import AuditLog
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.decisions import DecisionRepository
from solida.domain.ports.feature_store import FeatureStore
from solida.domain.ports.grille import GrilleRepository
from solida.domain.ports.modele import ScoringModel
from solida.domain.rules.capacite_remboursement import montant_maximal_supportable
from solida.domain.rules.cascade import ContexteCascade, ParametresCascade, determiner_mode
from solida.domain.rules.grille import decider
from solida.domain.rules.pre_verification import DIVISIBLE, OBJET_AUTRE, classe_objet
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
from solida.domain.values.features import FeaturesSolidaires
from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.montant import Montant
from solida.domain.values.motif_bascule import MotifBascule

AVERTISSEMENT_REVENU_MANQUANT = (
    "Le revenu mensuel est absent : les ratios associés ont été traités comme informations "
    "manquantes par le modèle."
)

AVERTISSEMENT_OBJET_AUTRE = (
    "Objet de crédit non classifié (« Autre ») : ce dossier doit être soumis au comité de "
    "crédit / à la conformité avant toute suite, quelle que soit la recommandation ci-contre."
)


def _avertissement_montant_reduit_objet_non_divisible(
    montant_demande: Montant,
    montant_recommande: Montant,
    objet_credit: str,
    classification_objets: Mapping[str, str],
) -> str | None:
    """J2-08 : un objet indivisible ou non classé ne peut pas s'accommoder d'un montant
    réduit (section 1.7) — l'agent doit le voir explicitement plutôt que le déduire."""
    if montant_recommande.valeur >= montant_demande.valeur:
        return None
    if classe_objet(objet_credit, classification_objets) == DIVISIBLE:
        return None
    return (
        f"Montant recommandé ({montant_recommande.valeur:,} FCFA) inférieur au montant "
        f"demandé ({montant_demande.valeur:,} FCFA) sur un objet non divisible : un montant "
        "réduit peut être inutilisable pour cet achat. Privilégier une durée plus longue, "
        "une garantie complémentaire ou un réexamen au prochain cycle."
    ).replace(",", " ")


# Alignée sur la durée de session pour bloquer un multi-octroi avant le reflet CORE-SIM.
FENETRE_MULTI_OCTROI = timedelta(hours=8)


@dataclass(frozen=True)
class ScorerDemande:
    core_sim_reader: CoreSimReader
    feature_store: FeatureStore
    scoring_model: ScoringModel
    scoring_model_enrichi: ScoringModel
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

    def _resoudre_mode(
        self, demande: DemandeScoring, date_reference: date
    ) -> tuple[ModeCalcul, MotifBascule | None, FeaturesSolidaires | None]:
        """Décide SOCLE vs enrichi (`cascade.determiner_mode`) à partir de l'historique réel
        du groupe emprunteur, jamais d'un tiers du groupe (arbitrage 2026-09-14)."""
        donnees_groupe = (
            self.core_sim_reader.charger_donnees_groupe(demande.groupe_id)
            if demande.groupe_id is not None
            else None
        )
        if donnees_groupe is None:
            contexte = ContexteCascade(
                appartient_a_un_groupe=False,
                taille_groupe=0,
                nb_credits_anterieurs_groupe_soldes=0,
                fraicheur_features_jours=0,
            )
        else:
            taille = taille_groupe_a_date(donnees_groupe.appartenances, date_reference)
            nb_soldes = sum(
                1
                for credit in donnees_groupe.credits_anterieurs
                if credit.date_deblocage < date_reference and credit.statut == "solde"
            )
            # Calculées à l'instant de la demande, jamais par un lot planifié (pas de
            # pipeline batch pour la couche solidaire, comme pour les features individuelles).
            contexte = ContexteCascade(
                appartient_a_un_groupe=True,
                taille_groupe=taille,
                nb_credits_anterieurs_groupe_soldes=nb_soldes,
                fraicheur_features_jours=0,
            )

        resultat = determiner_mode(contexte, ParametresCascade())
        if resultat.mode != ModeCalcul.ENRICHI:
            return resultat.mode, resultat.motif, None

        assert demande.groupe_id is not None  # garanti par `appartient_a_un_groupe`
        features_solidaires = self.feature_store.lire_solidaires(demande.groupe_id, date_reference)
        if features_solidaires is None:
            # Incohérence transitoire entre les deux lectures CORE-SIM (rarissime, pas de
            # concurrence en écriture attendue) : repli explicite plutôt qu'une décision
            # enrichie sans données plutôt qu'un crash.
            return ModeCalcul.SOCLE_SEUL, MotifBascule.SANS_GROUPE, None
        return ModeCalcul.ENRICHI, None, features_solidaires

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
        valider_montant_sous_plafond_institutionnel(
            demande.montant_demande, configuration.grille.plafond_institutionnel_fcfa
        )
        catalogue_produit = valider_produit_catalogue(
            self.core_sim_reader.charger_produits(), demande.produit_id
        )
        valider_duree_dans_bornes(demande.duree_demandee_mois, catalogue_produit)

        date_reference = datetime.now(UTC).date()
        features_individuelles = self.feature_store.lire_individuelles(
            demande.societaire_id, date_reference
        )
        if features_individuelles is None:
            raise DonneesInsuffisantes(
                f"Les données de {demande.societaire_id} ne permettent pas de calculer un score."
            )

        revenu_effectif = _revenu_effectif(demande, societaire.revenu_mensuel_declare)
        features_actualisees = _actualiser_features(
            features_individuelles, demande, revenu_effectif, catalogue_produit.taux_annuel
        )

        mode_calcul, motif_mode, features_solidaires = self._resoudre_mode(demande, date_reference)
        if mode_calcul == ModeCalcul.ENRICHI and features_solidaires is not None:
            features_dict = _features_to_dict_enrichi(
                features_actualisees, features_solidaires, demande
            )
            scoring_model = self.scoring_model_enrichi
            caution_deja_appelee = (features_solidaires.nb_cautions_appelees_anterieures or 0) > 0
        else:
            features_dict = _features_to_dict(features_actualisees, demande)
            scoring_model = self.scoring_model
            caution_deja_appelee = False

        try:
            probabilite = scoring_model.predire(features_dict)
            contributions_log_odds = scoring_model.contributions(features_dict)
        except ValueError as erreur:
            raise ModeleIndisponible(
                "Le moteur de scoring n'a pas pu produire de recommandation pour ce dossier. "
                "Réessayez dans quelques instants ; si le problème persiste, contactez le "
                "support technique avant de statuer manuellement sur cette demande."
            ) from erreur

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
        plafond_institutionnel = Montant(valeur=configuration.grille.plafond_institutionnel_fcfa)

        # Sans revenu connu, aucun plafond de capacité n'est calculé : décision terrain déjà
        # actée, un revenu manquant ne réduit ni ne refuse rien automatiquement.
        montant_recommande = montant_demande_v
        if revenu_effectif is not None and revenu_effectif > 0:
            plafond_capacite = montant_maximal_supportable(
                revenu_mensuel=revenu_effectif,
                duree_mois=demande.duree_demandee_mois,
                taux_annuel=catalogue_produit.taux_annuel,
                ratio_endettement_maximal=configuration.grille.ratio_endettement_maximal,
            )
            if plafond_capacite.valeur < montant_recommande.valeur:
                montant_recommande = plafond_capacite

        situation = SituationReexamen(
            regularite_epargne=features_actualisees.nb_mois_avec_depot_12m / 12,
            ratio_garantie=features_actualisees.ratio_epargne_montant,
            endettement=features_actualisees.ratio_endettement,
            tendance_epargne_baissiere=features_actualisees.tendance_epargne_12m == "erosion",
            caution_deja_appelee=caution_deja_appelee,
            montant_demande=montant_demande_v,
        )
        conditions = lister_conditions_reexamen(
            situation, ParametresReexamen(), configuration.grille.ratio_endettement_maximal
        )

        avertissement_montant_reduit = _avertissement_montant_reduit_objet_non_divisible(
            montant_demande_v,
            montant_recommande,
            demande.objet_credit,
            configuration.classification_objets,
        )

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
            montant_recommande=montant_recommande,
            mode_calcul=mode_calcul,
            motif_mode=motif_mode,
            points_de_base=points_de_base,
            decomposition=points,
            # Contrat conservé : le champ historique ne porte plus une progression.
            plafond_progressif=plafond_institutionnel,
            trajectoire_progression=[],
            conditions_reexamen=conditions,
            avertissements=[
                *([AVERTISSEMENT_OBJET_AUTRE] if demande.objet_credit == OBJET_AUTRE else []),
                *([AVERTISSEMENT_REVENU_MANQUANT] if revenu_effectif is None else []),
                *([avertissement_montant_reduit] if avertissement_montant_reduit else []),
            ],
            version_modele=scoring_model.version(),
            version_grille=configuration.version_grille,
        )
