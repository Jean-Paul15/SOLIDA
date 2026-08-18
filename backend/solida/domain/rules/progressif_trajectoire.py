from solida.domain.rules.progressif_plafond import ParametresProgressif, _modulation_risque
from solida.domain.values.montant import Montant
from solida.domain.values.palier_progression import PalierProgression
from solida.domain.values.probabilite import ProbabiliteDefaut


def calculer_trajectoire(
    plafond_actuel: Montant,
    probabilite: ProbabiliteDefaut,
    parametres: ParametresProgressif,
    plafond_produit: Montant,
    nb_cycles: int = 1,
) -> list[PalierProgression]:
    """Palier indicatif au prochain cycle, à profil de risque inchangé — jamais une
    décision prise à l'avance. Voir docs/formules/."""
    modulation = _modulation_risque(probabilite, parametres)
    trajectoire = []
    plafond: float = plafond_actuel.valeur
    for cycle in range(1, nb_cycles + 1):
        plafond = min(
            plafond * parametres.coefficient_progression * modulation, plafond_produit.valeur
        )
        trajectoire.append(
            PalierProgression(cycle=cycle, plafond_accessible=Montant(valeur=int(round(plafond))))
        )
    return trajectoire
