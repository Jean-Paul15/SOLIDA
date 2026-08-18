from solida.application.use_cases.consulter_dossier import ConsulterDossier
from solida.application.use_cases.lister_societaires_recents import ListerSocietairesRecents
from solida.application.use_cases.rechercher_societaire import RechercherSocietaire
from solida.infrastructure.dependances.adapters import audit_log, lecteur


def rechercher_societaire() -> RechercherSocietaire:
    return RechercherSocietaire(lecteur=lecteur())


def consulter_dossier() -> ConsulterDossier:
    return ConsulterDossier(lecteur=lecteur())


def lister_societaires_recents() -> ListerSocietairesRecents:
    return ListerSocietairesRecents(lecteur=lecteur(), audit_log=audit_log())
