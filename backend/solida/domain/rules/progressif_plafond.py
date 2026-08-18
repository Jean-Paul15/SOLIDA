from dataclasses import dataclass

from solida.domain.values.montant import Montant
from solida.domain.values.probabilite import ProbabiliteDefaut


@dataclass(frozen=True)
class ParametresProgressif:
    """Réglage du crédit progressif — voir docs/formules/."""

    coefficient_progression: float
    montant_plancher: Montant
    plafond_primo_emprunteur: Montant
    plafonds_produits: dict[str, Montant]
    """Clé = `produit_id`, ajustable par la supervision."""
    modulation_base: float = 1.3
    modulation_pente: float = 2.0
    modulation_min: float = 0.4
    modulation_max: float = 1.2


def _modulation_risque(probabilite: ProbabiliteDefaut, parametres: ParametresProgressif) -> float:
    return min(
        max(
            parametres.modulation_base - parametres.modulation_pente * probabilite.valeur,
            parametres.modulation_min,
        ),
        parametres.modulation_max,
    )


def calculer_plafond(
    montant_max_rembourse: Montant | None,
    montant_demande: Montant,
    probabilite: ProbabiliteDefaut,
    parametres: ParametresProgressif,
    plafond_produit: Montant,
) -> Montant:
    """Borne le montant recommandé par le principe du crédit progressif.

    `montant_max_rembourse` à None signifie un primo-emprunteur (aucun crédit
    antérieur) : le plafond applique alors `plafond_primo_emprunteur`, pas la
    formule générale qui n'a pas de base historique à partir de laquelle progresser.

    `plafond_produit` est résolu par l'appelant (le produit demandé n'est pas
    connu de ce module pur) — voir `ParametresProgressif.plafonds_produits` côté
    configuration de grille.
    """
    plafond: float
    if montant_max_rembourse is None:
        plafond = min(parametres.plafond_primo_emprunteur.valeur, montant_demande.valeur)
    else:
        base = max(
            montant_max_rembourse.valeur * parametres.coefficient_progression,
            parametres.montant_plancher.valeur,
        )
        plafond = min(
            base * _modulation_risque(probabilite, parametres),
            plafond_produit.valeur,
            montant_demande.valeur,
        )

    montant_recommande = max(plafond, parametres.montant_plancher.valeur)
    return Montant(valeur=int(round(montant_recommande)))
