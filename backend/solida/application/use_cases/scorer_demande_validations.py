from datetime import datetime

from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.entities.societaire import Societaire
from solida.domain.errors import (
    AccesRefuse,
    DureeDemandeeInvalide,
    MontantDemandeInvalide,
    ProduitIntrouvable,
    SocietaireIntrouvable,
    SurEndettement,
)
from solida.domain.ports.decisions import DecisionRepository

PLAFOND_INSTITUTIONNEL_FCFA = 100_000_000
"""Décision terrain : aucun plafond par produit, maximum institutionnel unique."""


def valider_societaire_trouve(societaire: Societaire | None, societaire_id: str) -> Societaire:
    if societaire is None:
        raise SocietaireIntrouvable(
            f"Aucun sociétaire ne correspond à l'identifiant {societaire_id}."
        )
    return societaire


def valider_acces_agence(societaire: Societaire, agent_agence_id: str | None) -> None:
    if agent_agence_id is not None and societaire.agence != agent_agence_id:
        raise AccesRefuse("Ce sociétaire n'appartient pas à votre agence.")


def valider_pas_de_credit_en_cours(societaire: Societaire, societaire_id: str) -> None:
    if societaire.a_credit_en_cours:
        raise SurEndettement(
            f"Le sociétaire {societaire_id} a déjà un crédit en cours : un "
            "nouvel octroi ne peut pas être confirmé par ce canal."
        )


def valider_pas_de_multi_octroi(
    decision_repository: DecisionRepository,
    societaire_id: str,
    since: datetime,
    raw_input: dict[str, object],
) -> None:
    if decision_repository.existe_decision_accordee_depuis(societaire_id, since, raw_input):
        raise SurEndettement(
            f"Le sociétaire {societaire_id} a déjà une décision accordée récente en "
            "attente de reflet dans CORE-SIM : un nouvel octroi ne peut pas être confirmé."
        )


def valider_montant_sous_plafond_institutionnel(montant_demande: int) -> None:
    if montant_demande > PLAFOND_INSTITUTIONNEL_FCFA:
        raise MontantDemandeInvalide(
            f"Le montant demandé ({montant_demande:,} FCFA) dépasse le plafond institutionnel "
            f"de {PLAFOND_INSTITUTIONNEL_FCFA:,} FCFA."
        )


def valider_produit_catalogue(produits: list[ProduitCredit], produit_id: str) -> ProduitCredit:
    catalogue_produit = next((p for p in produits if p.produit_id == produit_id), None)
    if catalogue_produit is None:
        # CORE-SIM est la seule source des bornes de durée ; sans catalogue, on rejette.
        raise ProduitIntrouvable(
            f"Le produit {produit_id!r} n'a pas de catalogue de durées valide."
        )
    return catalogue_produit


def valider_duree_dans_bornes(duree_demandee_mois: int, catalogue_produit: ProduitCredit) -> None:
    if not (
        catalogue_produit.duree_min_mois <= duree_demandee_mois <= catalogue_produit.duree_max_mois
    ):
        raise DureeDemandeeInvalide(
            f"La durée demandée ({duree_demandee_mois} mois) sort des bornes de ce "
            f"produit ({catalogue_produit.duree_min_mois}-{catalogue_produit.duree_max_mois} "
            "mois)."
        )
