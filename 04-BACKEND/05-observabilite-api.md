# Observabilité de l'API

## Journalisation structurée

JSON, un événement par ligne, `structlog`.

**Champs obligatoires :** horodatage, niveau, message, identifiant de corrélation, module.
**Selon le contexte :** identifiant utilisateur, route, durée, code de statut, version du modèle.

**Interdits dans les journaux :** mot de passe, jeton, nom complet de sociétaire, montant lié à un
identifiant nominatif, contenu d'une fiche.

Un identifiant opaque suffit toujours au diagnostic. Cette discipline est ce qui distingue un
système exploitable dans une institution financière d'un prototype.

## Niveaux

| Niveau | Usage |
|---|---|
| `DEBUG` | Développement uniquement, jamais actif en production |
| `INFO` | Événements métier : scoring rendu, fiche générée, job terminé |
| `WARNING` | Dégradation : bascule en mode socle, feature périmée, imputation appliquée |
| `ERROR` | Échec d'une opération, avec conséquence pour l'utilisateur |
| `CRITICAL` | Indisponibilité du service |

## Métriques Prometheus

### Techniques

| Métrique | Type | Étiquettes |
|---|---|---|
| `solida_http_requetes_total` | compteur | route, méthode, statut |
| `solida_http_duree_secondes` | histogramme | route |
| `solida_db_connexions_actives` | jauge | base |

### Métier — les plus utiles

| Métrique | Type | Étiquettes |
|---|---|---|
| `solida_scorings_total` | compteur | mode, tranche, agence |
| `solida_score_distribution` | histogramme | mode |
| `solida_bascules_mode_socle_total` | compteur | motif |
| `solida_features_perimees_total` | compteur | — |
| `solida_invariant_score_viole_total` | compteur | — |
| `solida_ecart_recommandation_total` | compteur | sens |

`solida_invariant_score_viole_total` doit rester **à zéro**. Toute valeur non nulle est une alerte
majeure : la décomposition en points ne somme plus au score, donc la fiche de justification est
fausse.

`solida_ecart_recommandation_total` mesure les cas où l'agent décide autrement que la
recommandation. C'est un indicateur de pilotage, pas une anomalie.

## Sonde de santé

`GET /api/v1/sante` renvoie : état de la base SOLIDA, état de l'accès CORE-SIM, modèle chargé et sa
version, date du dernier rafraîchissement du feature store, état de MinIO.

Un seul endpoint qui répond à la question « est-ce que ça marche ? » sans avoir à ouvrir cinq
outils. Très utile en démonstration.

## Tableaux Grafana

| Tableau | Public | Contenu |
|---|---|---|
| Exploitation | Technique | Latences, taux d'erreur, connexions, mémoire |
| Métier | Direction IMF | Scorings par jour et par agence, répartition des tranches, taux d'écart |
| Modèle | Data | Distribution des scores, taux de bascule, dérive |

Le tableau **métier** est celui à montrer au jury : il traduit le système en indicateurs qu'une
direction d'IMF comprend.

## Périmètre hackathon

P0 : journalisation structurée. P2 : Prometheus, Grafana, sonde complète.

Le journal structuré dès le début coûte presque rien et sauve des heures de diagnostic à 2 h du
matin le jour 2. Les tableaux Grafana sont un bonus de démonstration, pas une nécessité.
