"""Coercion de date partagée entre les lecteurs CORE-SIM.

CORE-SIM stocke plusieurs colonnes de date en `timestamp` (héritage du générateur, qui
écrit des colonnes pandas `datetime64` via `to_sql`) : psycopg les retourne en
`datetime.datetime` alors que le domaine attend `datetime.date` (`Societaire.date_adhesion`,
`MouvementEpargne.date_operation`...). Cette fonction ramène la valeur au type attendu à la
frontière de l'adaptateur, une fois pour toutes, plutôt que de laisser chaque appelant du
domaine découvrir la comparaison invalide `datetime > date` à l'exécution.
"""

from datetime import date, datetime


def vers_date(valeur: date | datetime) -> date:
    if isinstance(valeur, datetime):
        return valeur.date()
    return valeur
