# Outils spécialisés retenus

Pas d'écran maison pour la supervision du modèle ou la dérive : des outils dédiés, éprouvés,
conteneurisables, plutôt qu'une réimplémentation partielle dans le frontend SOLIDA.

| Besoin | Outil recommandé | Rôle | Docker ? |
|---|---|---|---|
| Suivi des expériences & registre de modèles | MLflow | Versions du modèle, métriques, artefacts | Oui |
| Versioning des données & pipelines | DVC (+ MinIO) | Reproductibilité données/modèles | Oui (MinIO) |
| Détection de dérive (data drift / concept drift) | Evidently ou WhyLabs (open source) | PSI, distribution des features, alertes | Oui |
| Monitoring applicatif (API) | Prometheus + Grafana | Latence, erreurs, volume de scorings | Oui |
| Logs structurés | Loki ou simplement logs JSON | Audit technique | Oui |
| Alerting | Alertmanager / email simple | Prévenir quand la dérive dépasse un seuil | Oui |
