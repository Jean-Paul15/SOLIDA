"""Racine de composition : construit les adaptateurs concrets et les injecte dans les cas
d'usage. Seul ce module (avec `auth.py`) a le droit de connaître à la fois les ports du
domaine et leurs implémentations concrètes.
"""

from functools import lru_cache

from solida.adapters.core_sim.feature_store_core_sim import FeatureStoreCoreSim
from solida.adapters.core_sim.lecteur_postgres import LecteurCoreSimPostgres
from solida.adapters.ml.modele_constant import ModeleConstant
from solida.adapters.persistence.decisions_sql import DepotDecisionsSql
from solida.adapters.persistence.grille_sql import DepotGrilleSql
from solida.adapters.persistence.journal_audit_sql import JournalAuditSql
from solida.application.use_cases.consulter_dossier import ConsulterDossier
from solida.application.use_cases.generer_fiche import GenererFiche
from solida.application.use_cases.gerer_grille import LireGrilleActive, ModifierGrille
from solida.application.use_cases.lire_decision import LireDecision
from solida.application.use_cases.lister_decisions import ListerDecisions
from solida.application.use_cases.rechercher_societaire import RechercherSocietaire
from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.infrastructure.database import moteur_coresim, moteur_solida


@lru_cache
def _lecteur() -> LecteurCoreSimPostgres:
    return LecteurCoreSimPostgres(moteur_coresim())


@lru_cache
def _feature_store() -> FeatureStoreCoreSim:
    return FeatureStoreCoreSim(_lecteur())


@lru_cache
def _modele() -> ModeleConstant:
    return ModeleConstant()


@lru_cache
def _depot_decisions() -> DepotDecisionsSql:
    return DepotDecisionsSql(moteur_solida())


@lru_cache
def _depot_grille() -> DepotGrilleSql:
    return DepotGrilleSql(moteur_solida())


@lru_cache
def journal_audit() -> JournalAuditSql:
    return JournalAuditSql(moteur_solida())


def rechercher_societaire() -> RechercherSocietaire:
    return RechercherSocietaire(lecteur=_lecteur())


def consulter_dossier() -> ConsulterDossier:
    return ConsulterDossier(lecteur=_lecteur())


def scorer_demande() -> ScorerDemande:
    return ScorerDemande(
        lecteur=_lecteur(),
        feature_store=_feature_store(),
        modele=_modele(),
        depot_grille=_depot_grille(),
        depot_decisions=_depot_decisions(),
    )


def lire_decision() -> LireDecision:
    return LireDecision(depot=_depot_decisions())


def lister_decisions() -> ListerDecisions:
    return ListerDecisions(depot=_depot_decisions(), lecteur=_lecteur())


def generer_fiche() -> GenererFiche:
    return GenererFiche(depot_decisions=_depot_decisions(), lecteur=_lecteur())


def lire_grille_active() -> LireGrilleActive:
    return LireGrilleActive(depot=_depot_grille())


def modifier_grille() -> ModifierGrille:
    return ModifierGrille(depot=_depot_grille())
