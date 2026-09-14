from solida.application.use_cases.archiver_notification import ArchiverNotification
from solida.application.use_cases.assigner_notification import AssignerNotification
from solida.application.use_cases.lister_agents_agence import ListerAgentsAgence
from solida.application.use_cases.lister_notifications import ListerNotifications
from solida.infrastructure.dependencies.adapters import (
    core_sim_reader,
    demande_societaire_repository,
    utilisateur_repository,
)


def lister_notifications() -> ListerNotifications:
    return ListerNotifications(
        demande_societaire_repository=demande_societaire_repository(),
        core_sim_reader=core_sim_reader(),
    )


def archiver_notification() -> ArchiverNotification:
    return ArchiverNotification(demande_societaire_repository=demande_societaire_repository())


def assigner_notification() -> AssignerNotification:
    return AssignerNotification(
        demande_societaire_repository=demande_societaire_repository(),
        utilisateur_repository=utilisateur_repository(),
    )


def lister_agents_agence() -> ListerAgentsAgence:
    return ListerAgentsAgence(utilisateur_repository=utilisateur_repository())
