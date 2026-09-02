from solida.application.use_cases.consulter_dossier import ConsulterDossier
from solida.application.use_cases.lister_societaires_recents import ListerSocietairesRecents
from solida.application.use_cases.rechercher_societaire import RechercherSocietaire
from solida.infrastructure.dependencies.adapters import audit_log, core_sim_reader


def rechercher_societaire() -> RechercherSocietaire:
    return RechercherSocietaire(core_sim_reader=core_sim_reader())


def consulter_dossier() -> ConsulterDossier:
    return ConsulterDossier(core_sim_reader=core_sim_reader())


def lister_societaires_recents() -> ListerSocietairesRecents:
    return ListerSocietairesRecents(core_sim_reader=core_sim_reader(), audit_log=audit_log())
