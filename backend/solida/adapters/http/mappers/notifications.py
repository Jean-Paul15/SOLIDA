from solida.adapters.http.schemas import notifications as schema_notifications
from solida.adapters.http.schemas import scoring as schema_scoring
from solida.domain.values.demande_societaire import DemandeSocietaireAffichee


def demande_to_notification(
    affichee: DemandeSocietaireAffichee,
) -> schema_notifications.DemandeSocietaireNotification:
    demande = affichee.demande
    return schema_notifications.DemandeSocietaireNotification(
        demande_id=demande.demande_id,
        societaire_id=demande.societaire_id,
        societaire_nom=affichee.societaire_nom,
        agence_id=demande.agence_id,
        montant_demande=demande.montant_demande,
        objet_credit=demande.objet_credit,
        duree_mois=demande.duree_mois,
        produit_id=demande.produit_id,
        resultat=schema_scoring.ScoringResult.model_validate(demande.resultat),
        statut=demande.statut,
        cree_le=demande.cree_le.isoformat(),
        assigne_a_agent_id=demande.assigne_a_agent_id,
    )
