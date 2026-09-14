from solida.adapters.http.schemas import societaires as schema_societaires
from solida.domain.values.dossier import DossierSocietaire, SyntheseGroupe


def groupe_to_schema(groupe: SyntheseGroupe) -> schema_societaires.SyntheseGroupe:
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


def dossier_to_schema(dossier: DossierSocietaire) -> schema_societaires.DossierSocietaire:
    groupe = groupe_to_schema(dossier.groupe) if dossier.groupe is not None else None

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
                schema_societaires.PointSoldeMensuel(
                    mois=p.mois.isoformat(),
                    solde_fin_mois=p.solde_fin_mois,
                    total_depots=p.total_depots,
                    total_retraits=p.total_retraits,
                )
                for p in dossier.epargne.serie_solde_12m
            ],
        ),
        historique_credit=[
            schema_societaires.CreditResume(
                credit_id=c.credit_id,
                produit_id=c.produit_id,
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
