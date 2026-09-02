from solida.application.use_cases.lister_decisions import ListerDecisions
from solida.infrastructure.dependencies.adapters import core_sim_reader, decision_repository


def lister_decisions() -> ListerDecisions:
    return ListerDecisions(
        decision_repository=decision_repository(), core_sim_reader=core_sim_reader()
    )
