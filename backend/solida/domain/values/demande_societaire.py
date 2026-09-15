from dataclasses import dataclass
from datetime import datetime

from solida.domain.values.decision import DecisionAEnregistrer

STATUT_NOUVELLE = "nouvelle"
STATUT_ARCHIVEE = "archivee"


@dataclass(frozen=True)
class DemandeSocietaireACreer:
    demande_id: str
    societaire_id: str
    agence_id: str
    montant_demande: int
    objet_credit: str
    duree_mois: int
    produit_id: str
    resultat: DecisionAEnregistrer
    """La sérialisation HTTP (ScoringResult) se fait dans l'adaptateur de
    persistance, pas ici : le domaine ne connaît pas les schémas HTTP."""
    assigne_a_agent_id: str | None = None
    """L'agent habituel du sociétaire (`DecisionRepository.dernier_agent_reel`), affecté dès la
    création quand il existe. `None` sinon : la demande reste non assignée, le superviseur
    choisit, comme pour un sociétaire sans historique."""


@dataclass(frozen=True)
class DemandeSocietaire:
    demande_id: str
    societaire_id: str
    agence_id: str
    montant_demande: int
    objet_credit: str
    duree_mois: int
    produit_id: str
    resultat: dict[str, object]
    """Relu tel quel depuis la colonne JSONB (déjà au format ScoringResult)."""
    statut: str
    """nouvelle | archivee."""
    cree_le: datetime
    assigne_a_agent_id: str | None
    archivee_le: datetime | None
    archivee_par_agent_id: str | None


@dataclass(frozen=True)
class DemandeSocietaireAffichee:
    demande: DemandeSocietaire
    societaire_nom: str
