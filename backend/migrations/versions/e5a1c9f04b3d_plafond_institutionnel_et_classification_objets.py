"""plafond institutionnel, ratio d'endettement max et classification objets dans la grille

Revision ID: e5a1c9f04b3d
Revises: d3f9a1c6e824
Create Date: 2026-09-14 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "e5a1c9f04b3d"
down_revision: str | None = "d3f9a1c6e824"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Migration de donnees uniquement (seuils est deja JSONB libre, aucun ALTER TABLE necessaire).
#
# plafond_institutionnel_fcfa : deplace depuis la constante Python codee en dur
# `PLAFOND_INSTITUTIONNEL_FCFA` (docs/continuite/2026-09-13-constat-claude-plafonds.md)
# vers la grille, pour que la supervision puisse le modifier sans deploiement.
#
# classification_objets : table divisible/indivisible/mixte par objet de credit, demandee
# par le plan (section 1.7) mais jamais confirmee comme donnee metier reelle
# (modelisation/docs/decisions-socle.md, questionnaire-modele-enrichi.md). Demarre vide :
# aucun objet n'est classe tant qu'une vraie table n'est pas fournie par le metier.
#
# ratio_endettement_maximal : part maximale du revenu que la mensualite d'un nouveau credit
# peut representer, utilisee pour plafonner le montant recommande (capacite de
# remboursement). 0.33 est un repere generique de "taux d'effort" du credit a la
# consommation ; ni la page publique des credits FUCEC-Togo (fucec-togo.com/services/credits)
# ni le dispositif prudentiel BCEAO/UMOA consulte ne documentent de seuil individuel chiffre
# pour ce contexte precis. Valeur de demonstration explicitement signalee comme telle -- voir
# PLAN 72H/DECISION_MANQUANTE_ratio_endettement.md -- a valider par le comite de credit.
PLAFOND_INSTITUTIONNEL_INITIAL_FCFA = 100_000_000
RATIO_ENDETTEMENT_MAXIMAL_INITIAL = 0.33


def upgrade() -> None:
    op.execute(
        text("""
            UPDATE grille_decision
            SET seuils = seuils
                || jsonb_build_object('plafond_institutionnel_fcfa', :plafond)
                || jsonb_build_object('ratio_endettement_maximal', :ratio_endettement)
                || jsonb_build_object('classification_objets', :classification)
        """).bindparams(
            bindparam("plafond", value=PLAFOND_INSTITUTIONNEL_INITIAL_FCFA, type_=JSONB),
            bindparam("ratio_endettement", value=RATIO_ENDETTEMENT_MAXIMAL_INITIAL, type_=JSONB),
            bindparam("classification", value={}, type_=JSONB),
        )
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE grille_decision
        SET seuils = (seuils - 'plafond_institutionnel_fcfa')
            - 'ratio_endettement_maximal' - 'classification_objets'
        """
    )
