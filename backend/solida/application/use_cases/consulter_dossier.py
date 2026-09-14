from dataclasses import dataclass
from datetime import date

from solida.application.use_cases.consulter_dossier_mapping import (
    _alertes,
    _groupe_affiche,
    _ratio_epargne_revenu,
    _secteur,
)
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.rules.epargne import tendance_depuis_croissance
from solida.domain.values.dossier import (
    ActiviteEconomique,
    CreditResume,
    DossierSocietaire,
    IdentiteSocietaire,
    PointSoldeMensuel,
    SyntheseEpargne,
)

PROFONDEUR_SERIE_SOLDE_MOIS = 24
"""Cible du §5.2 : 24 mois, minimum 12 — la série sert aussi bien un horizon d'affichage
court (3 mois) qu'un futur horizon 24 mois sans changer le contrat."""

STATUT_SOCIETAIRE_PAR_DEFAUT = "actif"
"""Le générateur ne modélise ni churn ni radiation, voir `CoreSimPostgresReader`."""


@dataclass(frozen=True)
class ConsulterDossier:
    core_sim_reader: CoreSimReader

    def execute(self, societaire_id: str) -> DossierSocietaire | None:
        societaire = self.core_sim_reader.charger_societaire(societaire_id)
        if societaire is None:
            return None

        credits = self.core_sim_reader.charger_historique_credit(societaire_id)
        compte = self.core_sim_reader.charger_compte_epargne(societaire_id)
        groupe = _groupe_affiche(self.core_sim_reader.charger_groupe(societaire_id))
        soldes_mensuels = self.core_sim_reader.charger_soldes_mensuels(
            societaire_id, avant=date.today()
        )[-PROFONDEUR_SERIE_SOLDE_MOIS:]

        historique = [
            CreditResume(
                credit_id=c.credit_id,
                produit_id=c.produit_id,
                date_deblocage=c.date_deblocage,
                montant_octroye=c.montant_octroye,
                duree_mois=c.duree_mois,
                numero_cycle=c.numero_cycle,
                statut=c.statut,
                capital_restant_du=c.capital_restant_du,
                max_jours_retard=c.jours_retard_max or 0,
            )
            for c in credits
        ]

        return DossierSocietaire(
            identite=IdentiteSocietaire(
                societaire_id=societaire.societaire_id,
                numero_membre=societaire.numero_membre,
                nom_complet=societaire.nom_complet,
                segment=societaire.segment,
                agence=societaire.agence,
                date_adhesion=societaire.date_adhesion,
                anciennete_mois=societaire.anciennete_mois,
                statut=STATUT_SOCIETAIRE_PAR_DEFAUT,
                age=societaire.age,
                niveau_instruction=societaire.niveau_instruction,
            ),
            activite=ActiviteEconomique(
                secteur=_secteur(societaire.segment),
                anciennete_activite_mois=societaire.anciennete_mois,
                revenu_mensuel_declare=societaire.revenu_mensuel_declare,
                charges_mensuelles=None,
                capacite_remboursement_estimee=societaire.revenu_mensuel_declare or 0,
                nb_personnes_a_charge=societaire.nb_personnes_a_charge,
                parts_sociales_montant=societaire.parts_sociales_montant,
            ),
            epargne=SyntheseEpargne(
                solde_moyen_6m=compte.solde_moyen_6m if compte else 0,
                tendance_12m=tendance_depuis_croissance(compte.croissance_12m if compte else 0.0),
                nb_mois_avec_depot_12m=compte.nb_mois_avec_depot_12m if compte else 0,
                volatilite=compte.volatilite if compte else 0.0,
                ratio_epargne_revenu=_ratio_epargne_revenu(
                    compte, societaire.revenu_mensuel_declare
                ),
                anciennete_relation_mois=societaire.anciennete_mois,
                serie_solde_12m=[
                    PointSoldeMensuel(
                        mois=s.mois,
                        solde_fin_mois=round(s.solde_fin_mois),
                        total_depots=round(s.total_depots),
                        total_retraits=round(s.total_retraits),
                    )
                    for s in soldes_mensuels
                ],
            ),
            historique_credit=historique,
            groupe=groupe,
            alertes=_alertes(historique, groupe),
        )
