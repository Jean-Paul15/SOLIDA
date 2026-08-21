from solida.application.use_cases.lister_decisions import ListerDecisions
from solida.infrastructure.dependencies.adapters import decision_repository, lecteur


def lister_decisions() -> ListerDecisions:
    return ListerDecisions(decision_repository=decision_repository(), lecteur=lecteur())
