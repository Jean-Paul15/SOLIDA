"""Conversion des value objects du domaine vers les schémas pydantic exposés en HTTP.

Centralisé ici plutôt que dispersé dans chaque routeur : un seul endroit à vérifier quand
un champ du contrat frontend change.
"""

from solida.adapters.http.schemas import fiche as schema_fiche
from solida.adapters.http.schemas import grille as schema_grille
from solida.adapters.http.schemas import registre as schema_registre
from solida.adapters.http.schemas import scoring as schema_scoring
from solida.adapters.http.schemas import societaires as schema_societaires
from solida.domain.values.decision import DecisionEnregistree, DecisionRegistreAffichee
from solida.domain.values.dossier import DossierSocietaire, SyntheseGroupe
from solida.domain.values.fiche import EnTeteFiche
from solida.domain.values.grille import ConfigurationGrille


def decision_vers_resultat_scoring(decision: DecisionEnregistree) -> schema_scoring.ResultatScoring:
    montant_demande = decision.entree.get("montant_demande")
    montant_demande_int = montant_demande if isinstance(montant_demande, int) else 0
    return schema_scoring.ResultatScoring(
        decision_id=decision.decision_id,
        societaire_id=decision.societaire_id,
        score=decision.score.valeur,
        tranche=decision.tranche.value,
        montant_recommande=decision.montant_recommande.valeur,
        montant_demande=montant_demande_int,
        mode_calcul=decision.mode_calcul.value,
        motif_mode=decision.motif_mode.value if decision.motif_mode else None,
        decomposition=[],  # ModeleConstant ne produit aucune contribution par variable.
        points_de_base=decision.points_de_base,
        plafond_progressif=decision.plafond_progressif.valeur,
        trajectoire_progression=[
            schema_scoring.PalierProgression(
                cycle=p.cycle, plafond_accessible=p.plafond_accessible.valeur
            )
            for p in decision.trajectoire_progression
        ],
        conditions_reexamen=decision.conditions_reexamen,
        version_modele=decision.version_modele,
        version_grille=decision.version_grille,
        horodatage=decision.horodatage.isoformat(),
        avertissements=decision.avertissements,
    )


def decision_vers_registre(
    affichee: DecisionRegistreAffichee,
) -> schema_registre.DecisionRegistre:
    decision = affichee.decision
    return schema_registre.DecisionRegistre(
        decision_id=decision.decision_id,
        societaire_id=decision.societaire_id,
        societaire_nom=affichee.societaire_nom,
        agence=affichee.agence,
        demande=schema_scoring.EntreeScoring(**decision.entree),
        resultat=decision_vers_resultat_scoring(decision),
        horodatage=decision.horodatage.isoformat(),
        agent_nom=decision.agent_nom,
    )


def groupe_vers_schema(groupe: SyntheseGroupe) -> schema_societaires.SyntheseGroupe:
    return schema_societaires.SyntheseGroupe(
        groupe_id=groupe.groupe_id,
        nom_groupe=groupe.nom_groupe,
        taille_actuelle=groupe.taille_actuelle,
        date_creation=groupe.date_creation.isoformat(),
        taux_remboursement_groupe=groupe.taux_remboursement_groupe,
        nb_cycles_completes=groupe.nb_cycles_completes,
        nb_sorties_12m=groupe.nb_sorties_12m,
        statut=groupe.statut,
        membres=[
            schema_societaires.MembreGroupe(
                societaire_id=m.societaire_id,
                nom_complet=m.nom_complet,
                role=m.role,
                anciennete_mois=m.anciennete_mois,
                statut_credit=m.statut_credit,
                caution_appelee=m.caution_appelee,
            )
            for m in groupe.membres
        ],
    )


def dossier_vers_schema(dossier: DossierSocietaire) -> schema_societaires.DossierSocietaire:
    groupe = groupe_vers_schema(dossier.groupe) if dossier.groupe is not None else None

    return schema_societaires.DossierSocietaire(
        identite=schema_societaires.IdentiteSocietaire(
            societaire_id=dossier.identite.societaire_id,
            numero_membre=dossier.identite.numero_membre,
            nom_complet=dossier.identite.nom_complet,
            segment=dossier.identite.segment,
            agence=dossier.identite.agence,
            date_adhesion=dossier.identite.date_adhesion.isoformat(),
            anciennete_mois=dossier.identite.anciennete_mois,
            statut=dossier.identite.statut,
            age=dossier.identite.age,
            niveau_instruction=dossier.identite.niveau_instruction,
        ),
        activite=schema_societaires.ActiviteEconomique(
            secteur=dossier.activite.secteur,
            anciennete_activite_mois=dossier.activite.anciennete_activite_mois,
            revenu_mensuel_declare=dossier.activite.revenu_mensuel_declare,
            charges_mensuelles=dossier.activite.charges_mensuelles,
            capacite_remboursement_estimee=dossier.activite.capacite_remboursement_estimee,
            nb_personnes_a_charge=dossier.activite.nb_personnes_a_charge,
            parts_sociales_montant=dossier.activite.parts_sociales_montant,
        ),
        epargne=schema_societaires.SyntheseEpargne(
            solde_moyen_6m=dossier.epargne.solde_moyen_6m,
            tendance_12m=dossier.epargne.tendance_12m,
            nb_mois_avec_depot_12m=dossier.epargne.nb_mois_avec_depot_12m,
            volatilite=dossier.epargne.volatilite,
            ratio_epargne_revenu=dossier.epargne.ratio_epargne_revenu,
            anciennete_relation_mois=dossier.epargne.anciennete_relation_mois,
            serie_solde_12m=[
                schema_societaires.PointSolde(mois=p.mois, solde=p.solde)
                for p in dossier.epargne.serie_solde_12m
            ],
        ),
        historique_credit=[
            schema_societaires.CreditResume(
                credit_id=c.credit_id,
                date_deblocage=c.date_deblocage.isoformat(),
                montant_octroye=c.montant_octroye,
                duree_mois=c.duree_mois,
                numero_cycle=c.numero_cycle,
                statut=c.statut,
                capital_restant_du=c.capital_restant_du,
                max_jours_retard=c.max_jours_retard,
            )
            for c in dossier.historique_credit
        ],
        groupe=groupe,
        alertes=dossier.alertes,
    )


def fiche_vers_schema(
    decision: DecisionEnregistree, entete: EnTeteFiche
) -> schema_fiche.FicheJustification:
    return schema_fiche.FicheJustification(
        fiche_id=decision.decision_id,
        resultat=decision_vers_resultat_scoring(decision),
        demande=schema_scoring.EntreeScoring(**decision.entree),
        societaire_nom=entete.societaire_nom,
        numero_membre=entete.numero_membre,
        agence=entete.agence,
        agent_nom=decision.agent_nom,
        date_edition=entete.date_edition.isoformat(),
        facteurs_favorables=[],
        facteurs_defavorables=[],
        conditions_reexamen=decision.conditions_reexamen,
        mention_legale=entete.mention_legale,
    )


def grille_vers_schema(configuration: ConfigurationGrille) -> schema_grille.ConfigurationGrille:
    return schema_grille.ConfigurationGrille(
        version_grille=configuration.version_grille,
        grille=schema_grille.ParametresGrille(
            marge=configuration.grille.marge,
            lgd=configuration.grille.lgd,
            multiplicateur_accord=configuration.grille.multiplicateur_accord,
            multiplicateur_vigilance=configuration.grille.multiplicateur_vigilance,
            multiplicateur_examen=configuration.grille.multiplicateur_examen,
        ),
        progressif=schema_grille.ParametresProgressif(
            coefficient_progression=configuration.progressif.coefficient_progression,
            montant_plancher=configuration.progressif.montant_plancher.valeur,
            plafond_produit=configuration.progressif.plafond_produit.valeur,
            plafond_primo_emprunteur=configuration.progressif.plafond_primo_emprunteur.valeur,
            modulation_base=configuration.progressif.modulation_base,
            modulation_pente=configuration.progressif.modulation_pente,
            modulation_min=configuration.progressif.modulation_min,
            modulation_max=configuration.progressif.modulation_max,
        ),
        scorecard=schema_grille.ParametresScorecard(
            pdo=configuration.scorecard.pdo,
            score_reference=configuration.scorecard.score_reference,
            odds_reference=configuration.scorecard.odds_reference,
        ),
        auteur=configuration.auteur,
        date_activation=configuration.date_activation.isoformat(),
        active=configuration.active,
    )
