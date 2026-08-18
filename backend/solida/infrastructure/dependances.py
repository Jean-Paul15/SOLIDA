"""Racine de composition : construit les adaptateurs concrets et les injecte dans les cas
d'usage. Seul ce module (avec `auth.py`) a le droit de connaître à la fois les ports du
domaine et leurs implémentations concrètes.
"""

from functools import lru_cache

from minio import Minio

from solida.adapters.core_sim.feature_store_core_sim import FeatureStoreCoreSim
from solida.adapters.core_sim.lecteur_postgres import LecteurCoreSimPostgres
from solida.adapters.ml.modele_constant import ModeleConstant
from solida.adapters.pdf.rendu_fiche import GenerateurFichePdfWeasyPrint
from solida.adapters.persistence.decision_repository_sql import SqlDecisionRepository
from solida.adapters.persistence.fiche_archivee_repository_sql import SqlFicheArchiveeRepository
from solida.adapters.persistence.grille_repository_sql import SqlGrilleRepository
from solida.adapters.persistence.journal_audit_sql import JournalAuditSql
from solida.adapters.storage.fiche_repository_seaweedfs import SeaweedfsFicheRepository
from solida.application.use_cases.archiver_fiche import ArchiverFiche
from solida.application.use_cases.consulter_dossier import ConsulterDossier
from solida.application.use_cases.generer_fiche import GenererFiche
from solida.application.use_cases.gerer_grille import LireGrilleActive, ModifierGrille
from solida.application.use_cases.lire_decision import LireDecision
from solida.application.use_cases.lister_decisions import ListerDecisions
from solida.application.use_cases.lister_produits import ListerProduits
from solida.application.use_cases.lister_societaires_recents import ListerSocietairesRecents
from solida.application.use_cases.rechercher_societaire import RechercherSocietaire
from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.infrastructure.config import Configuration
from solida.infrastructure.database import coresim_engine, solida_engine


@lru_cache
def _lecteur() -> LecteurCoreSimPostgres:
    return LecteurCoreSimPostgres(coresim_engine())


@lru_cache
def _feature_store() -> FeatureStoreCoreSim:
    return FeatureStoreCoreSim(_lecteur())


@lru_cache
def _modele() -> ModeleConstant:
    return ModeleConstant()


@lru_cache
def _decision_repository() -> SqlDecisionRepository:
    return SqlDecisionRepository(solida_engine())


@lru_cache
def _grille_repository() -> SqlGrilleRepository:
    return SqlGrilleRepository(solida_engine())


@lru_cache
def journal_audit() -> JournalAuditSql:
    return JournalAuditSql(solida_engine())


@lru_cache
def _client_seaweedfs() -> Minio:
    configuration = Configuration()
    return Minio(
        configuration.seaweedfs_endpoint,
        access_key=configuration.seaweedfs_access_key,
        secret_key=configuration.seaweedfs_secret_key,
        secure=False,
    )


@lru_cache
def _fiche_repository() -> SeaweedfsFicheRepository:
    configuration = Configuration()
    return SeaweedfsFicheRepository(_client_seaweedfs(), configuration.seaweedfs_bucket)


@lru_cache
def _fiche_archivee_repository() -> SqlFicheArchiveeRepository:
    return SqlFicheArchiveeRepository(solida_engine())


@lru_cache
def _generateur_fiche_pdf() -> GenerateurFichePdfWeasyPrint:
    return GenerateurFichePdfWeasyPrint()


def rechercher_societaire() -> RechercherSocietaire:
    return RechercherSocietaire(lecteur=_lecteur())


def consulter_dossier() -> ConsulterDossier:
    return ConsulterDossier(lecteur=_lecteur())


def lister_societaires_recents() -> ListerSocietairesRecents:
    return ListerSocietairesRecents(lecteur=_lecteur(), journal_audit=journal_audit())


def scorer_demande() -> ScorerDemande:
    return ScorerDemande(
        lecteur=_lecteur(),
        feature_store=_feature_store(),
        modele=_modele(),
        grille_repository=_grille_repository(),
        decision_repository=_decision_repository(),
        journal_audit=journal_audit(),
    )


def lire_decision() -> LireDecision:
    return LireDecision(decision_repository=_decision_repository())


def lister_decisions() -> ListerDecisions:
    return ListerDecisions(decision_repository=_decision_repository(), lecteur=_lecteur())


def generer_fiche() -> GenererFiche:
    return GenererFiche(decision_repository=_decision_repository(), lecteur=_lecteur())


def generateur_fiche_pdf() -> GenerateurFichePdfWeasyPrint:
    return _generateur_fiche_pdf()


def archiver_fiche() -> ArchiverFiche:
    return ArchiverFiche(
        generer_fiche=generer_fiche(),
        generateur_pdf=_generateur_fiche_pdf(),
        fiche_repository=_fiche_repository(),
        fiche_archivee_repository=_fiche_archivee_repository(),
        journal_audit=journal_audit(),
    )


def lire_grille_active() -> LireGrilleActive:
    return LireGrilleActive(grille_repository=_grille_repository())


def modifier_grille() -> ModifierGrille:
    return ModifierGrille(grille_repository=_grille_repository())


def lister_produits() -> ListerProduits:
    return ListerProduits(lecteur=_lecteur(), grille_repository=_grille_repository())
