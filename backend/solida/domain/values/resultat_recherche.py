from dataclasses import dataclass


@dataclass(frozen=True)
class ResultatRechercheSocietaire:
    societaire_id: str
    nom_complet: str
    numero_membre: str
    agence: str
    zone: str
    statut: str
    a_credit_en_cours: bool
