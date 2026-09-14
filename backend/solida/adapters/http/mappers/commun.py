from solida.adapters.http import libelles_variables
from solida.adapters.http.schemas import scoring as schema_scoring
from solida.domain.values.features import ValeurFeature
from solida.domain.values.points_variable import PointsVariable


def _decomposition_to_schema(
    decomposition: list[PointsVariable], features_utilisees: dict[str, ValeurFeature]
) -> list[schema_scoring.ContributionVariable]:
    contributions = []
    for point in decomposition:
        valeur_brute = features_utilisees.get(point.code_variable)
        valeur_affichee = libelles_variables.formater_valeur(point.code_variable, valeur_brute)
        contributions.append(
            schema_scoring.ContributionVariable(
                code_variable=point.code_variable,
                libelle=libelles_variables.libelle(point.code_variable),
                valeur=valeur_affichee,
                points=point.points,
                sens=libelles_variables.sens(point.points),
                famille=libelles_variables.famille(point.code_variable),
                explication=libelles_variables.explication(point.points),
            )
        )
    # Les facteurs les plus déterminants d'abord : c'est ce que "Facteurs déterminants" promet.
    contributions.sort(key=lambda c: abs(c.points), reverse=True)
    return contributions
