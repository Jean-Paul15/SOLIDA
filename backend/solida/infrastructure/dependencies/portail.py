from solida.application.use_cases.authenticate_societaire import AuthenticateSocietaire
from solida.application.use_cases.process_societaire_demande import ProcessSocietaireDemande
from solida.infrastructure.dependencies.adapters import (
    core_sim_reader,
    demande_societaire_repository,
    notification_sender,
    secret_auth,
)
from solida.infrastructure.dependencies.scoring import scorer_demande


def authenticate_societaire() -> AuthenticateSocietaire:
    return AuthenticateSocietaire(core_sim_reader=core_sim_reader(), secret=secret_auth())


def process_societaire_demande() -> ProcessSocietaireDemande:
    return ProcessSocietaireDemande(
        core_sim_reader=core_sim_reader(),
        scorer_demande=scorer_demande(),
        demande_societaire_repository=demande_societaire_repository(),
        notification_sender=notification_sender(),
        secret=secret_auth(),
    )
