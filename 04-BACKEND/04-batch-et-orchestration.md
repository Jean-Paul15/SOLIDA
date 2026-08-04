# Batch et orchestration

## Rôle du batch

Le batch porte tout ce qui est coûteux, afin que le guichet reste rapide. Voir
`01-ARCHITECTURE/06`.

| Job | Fréquence | Durée cible |
|---|---|---|
| `copier_tables_solidaires` | Nocturne | < 5 min |
| `calculer_features_individuelles` | Nocturne | < 10 min |
| `calculer_features_solidaires` | Nocturne | < 15 min |
| `rafraichir_index_recherche` | Nocturne | < 2 min |
| `controler_derive` | Hebdomadaire | < 5 min |

Sur le volume simulé, ces cibles sont largement atteignables. Elles servent de garde-fou : un job
qui les dépasse signale une requête mal indexée.

## Orchestrateur

**Décision : APScheduler ou une simple tâche cron, pas Airflow.**

Airflow est un outil remarquable et une charge d'exploitation considérable : ordonnanceur, base de
métadonnées, exécuteurs, interface web. Pour cinq jobs séquentiels dans une coopérative, c'est
disproportionné et cela contredit l'argument de légèreté que nous défendons devant le jury.

Un mentor pourra demander pourquoi pas Airflow. La réponse est celle-ci, et elle est solide.
À documenter comme évolution si le réseau CIF centralise un jour le traitement pour plusieurs
coopératives.

## Propriétés exigées de chaque job

| Propriété | Signification |
|---|---|
| **Idempotent** | Deux exécutions successives donnent le même état final |
| **Reprenable** | Une interruption ne laisse pas la base dans un état incohérent |
| **Journalisé** | Début, fin, volumétrie, durée, erreurs |
| **Observable** | Métriques exposées à Prometheus |
| **Isolé** | L'échec d'un job n'empêche pas les autres, sauf dépendance déclarée |

L'idempotence est la propriété la plus importante : quand un job échoue à 3 h du matin, on veut
pouvoir le relancer sans se demander dans quel état il a laissé les données.

## Enchaînement

```
copier_tables_solidaires
      │
      ├──► calculer_features_individuelles ──┐
      │                                       │
      └──► calculer_features_solidaires ──┤
                                              │
                                              ▼
                                  rafraichir_index_recherche
```

Les deux calculs de features sont indépendants et peuvent tourner en parallèle. Si le calcul de la
couche solidaire échoue, l'individuel reste valide : le système bascule simplement en mode socle
pour tout le monde le lendemain. **Dégradation gracieuse, pas panne.**

## Écriture transactionnelle

Chaque job écrit dans une table temporaire puis bascule en une transaction. Ainsi, le feature store
n'est jamais partiellement à jour pendant que des agents scorent.

## Fraîcheur

Chaque enregistrement du feature store porte `date_calcul`. L'API expose cette date, et
l'interface l'affiche (« Données consolidées le … »).

**Seuil d'alerte : 7 jours.** Au-delà, le mode enrichi est désactivé et un avertissement est
affiché. Scorer avec des données de groupe vieilles d'un mois vaut moins que de dire qu'on ne les a
pas.

## Périmètre hackathon

P0 : les jobs sont des scripts lancés manuellement, avec journalisation.
P1 : orchestration et enchaînement automatique.
P2 : ordonnancement, métriques, alertes.

Lancer les jobs à la main pendant les 72 heures est parfaitement acceptable et se démontre très
bien : « voici le traitement nocturne, je le déclenche devant vous ».
