from typing import Protocol


class JournalAudit(Protocol):
    """Chaque entrée : acteur, action, objet, horodatage. Jamais de mot de passe,
    jeton, nom complet de sociétaire ou montant associé à un identifiant
    nominatif dans `details` — les identifiants opaques suffisent au diagnostic.
    """

    def enregistrer_evenement(
        self,
        type_evenement: str,
        acteur_id: str,
        objet: str,
        details: dict[str, object],
    ) -> None: ...
