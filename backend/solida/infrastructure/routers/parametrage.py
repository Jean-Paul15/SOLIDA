from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from solida.adapters.http import mappers
from solida.adapters.http.schemas.grille import ConfigurationGrille, NouvelleConfigurationGrille
from solida.adapters.persistence.orm_models import User
from solida.application.use_cases.gerer_grille import LireGrilleActive, ModifierGrille
from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard
from solida.domain.values.grille import ConfigurationGrille as ConfigurationGrilleDomaine
from solida.domain.values.montant import Montant
from solida.infrastructure.auth.dependencies import require_role
from solida.infrastructure.dependencies import lire_grille_active, modifier_grille

router = APIRouter(prefix="/api/v1/parametrage", tags=["parametrage"])

ROLES_LECTURE_GRILLE = ("superviseur", "auditeur", "administrateur", "agent")
"""Lecture seule, y compris pour l'agent : il doit pouvoir situer un score par rapport aux
seuils de la grille qui a produit sa décision (explicabilité), sans pouvoir la modifier —
`POST /grille` (ci-dessous) reste réservé à la supervision."""


@router.get("/grille", response_model=ConfigurationGrille)
def lire(
    user: User = Depends(require_role(*ROLES_LECTURE_GRILLE)),
    use_case: LireGrilleActive = Depends(lire_grille_active),
) -> ConfigurationGrille:
    return mappers.grille_to_schema(use_case.execute())


@router.post("/grille", response_model=ConfigurationGrille)
def modifier(
    nouvelle: NouvelleConfigurationGrille,
    user: User = Depends(require_role("superviseur")),
    use_case: ModifierGrille = Depends(modifier_grille),
) -> ConfigurationGrille:
    configuration = ConfigurationGrilleDomaine(
        version_grille=nouvelle.version_grille,
        grille=ParametresGrille(
            marge=nouvelle.grille.marge,
            lgd=nouvelle.grille.lgd,
            multiplicateur_accord=nouvelle.grille.multiplicateur_accord,
            plafond_institutionnel_fcfa=nouvelle.grille.plafond_institutionnel_fcfa,
            ratio_endettement_maximal=nouvelle.grille.ratio_endettement_maximal,
        ),
        progressif=ParametresProgressif(
            coefficient_progression=nouvelle.progressif.coefficient_progression,
            montant_plancher=Montant(valeur=nouvelle.progressif.montant_plancher),
            plafond_primo_emprunteur=Montant(valeur=nouvelle.progressif.plafond_primo_emprunteur),
            plafonds_produits={
                produit_id: Montant(valeur=montant)
                for produit_id, montant in nouvelle.progressif.plafonds_produits.items()
            },
            modulation_base=nouvelle.progressif.modulation_base,
            modulation_pente=nouvelle.progressif.modulation_pente,
            modulation_min=nouvelle.progressif.modulation_min,
            modulation_max=nouvelle.progressif.modulation_max,
        ),
        scorecard=ParametresScorecard(
            pdo=nouvelle.scorecard.pdo,
            score_reference=nouvelle.scorecard.score_reference,
            odds_reference=nouvelle.scorecard.odds_reference,
            score_min=300,
            score_max=850,
        ),
        # date_activation et active sont recalcules par le depot (server_default en base) :
        # les valeurs ici ne servent qu'a satisfaire le typage du value object.
        auteur=user.nom_complet,
        date_activation=datetime.now(UTC),
        active=True,
    )
    return mappers.grille_to_schema(use_case.execute(configuration))
