from dataclasses import dataclass


@dataclass(frozen=True)
class ActualisationSituation:
    revenu_mensuel_declare: int | None = None
    charges_mensuelles: int | None = None
    nb_personnes_a_charge: int | None = None


@dataclass(frozen=True)
class DemandeScoring:
    societaire_id: str
    produit_id: str
    montant_demande: int
    duree_demandee_mois: int
    objet_credit: str
    groupe_id: str | None
    actualisation: ActualisationSituation | None
