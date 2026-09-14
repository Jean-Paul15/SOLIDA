"""Données de démonstration pour `cli_provisionner_comptes demo` — jamais de vrais comptes,
isolées ici pour que leur nature de fixture reste sans ambiguïté."""

MOT_DE_PASSE_DEMO = "solida-demo"

COMPTES_DEMO: list[dict[str, str | None]] = [
    {
        "identifiant": "agent.be",
        "email": "agent.be@solida.local",
        "nom_complet": "Agent Bè",
        "role": "agent",
        "agence_id": "CAI-00",
    },
    {
        "identifiant": "agent.agoe",
        "email": "agent.agoe@solida.local",
        "nom_complet": "Agent Agoè",
        "role": "agent",
        "agence_id": "CAI-01",
    },
    {
        "identifiant": "superviseur.reseau",
        "email": "superviseur.reseau@solida.local",
        "nom_complet": "Superviseur Réseau",
        "role": "superviseur",
        "agence_id": None,
    },
    {
        "identifiant": "superviseur.cai00",
        "email": "superviseur.cai00@solida.local",
        "nom_complet": "Superviseure Bè",
        "role": "superviseur",
        "agence_id": "CAI-00",
    },
    {
        "identifiant": "auditeur.interne",
        "email": "auditeur.interne@solida.local",
        "nom_complet": "Auditeur Interne",
        "role": "auditeur",
        "agence_id": None,
    },
    {
        "identifiant": "administrateur.systeme",
        "email": "administrateur.systeme@solida.local",
        "nom_complet": "Administrateur Système",
        "role": "administrateur",
        "agence_id": None,
    },
]
