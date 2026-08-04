from dataclasses import dataclass
from datetime import datetime

MENTION_LEGALE = (
    "Cette fiche restitue une décision indicative produite par un système d'aide à la "
    "décision ; elle ne constitue pas un engagement de crédit et reste soumise à la "
    "validation finale de la coopérative."
)


@dataclass(frozen=True)
class EnTeteFiche:
    """Ce que `generer_fiche` ajoute à la décision déjà persistée pour composer la fiche :
    tout le reste (résultat, demande) vient de `DecisionEnregistree`, pas dupliqué ici.
    """

    societaire_nom: str
    numero_membre: str
    agence: str
    date_edition: datetime
    mention_legale: str
