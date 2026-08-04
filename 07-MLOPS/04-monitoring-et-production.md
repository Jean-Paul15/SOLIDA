# Monitoring et mise en production

## Ce qu'on surveille, par question posée

| Question | Indicateur |
|---|---|
| Le service répond-il ? | Sonde de santé, taux d'erreur HTTP |
| Est-il assez rapide ? | Latence p95 du scoring |
| Le modèle fonctionne-t-il ? | Taux de scorings aboutis, violations d'invariant |
| Le modèle est-il toujours pertinent ? | PSI, distribution des scores |
| Les données sont-elles fraîches ? | Âge du feature store |
| Les agents suivent-ils la recommandation ? | Taux d'écart |
| La couche solidaire est-elle exploitable ? | Taux de bascule en mode socle |

Les trois derniers sont spécifiques à SOLIDA et sont ceux qui intéresseront une direction d'IMF.

## Seuils d'alerte

| Indicateur | Avertissement | Alerte |
|---|---|---|
| Latence p95 scoring | > 1 s | > 3 s |
| Taux d'erreur HTTP | > 1 % | > 5 % |
| Violations d'invariant | ≥ 1 | ≥ 1 |
| Âge du feature store | > 3 jours | > 7 jours |
| Taux de bascule socle | > 40 % | > 60 % |
| Taux d'écart à la recommandation | > 25 % | > 40 % |

Une seule violation d'invariant est immédiatement une alerte : cela signifie qu'une fiche de
justification a pu être fausse.

## Déploiement

| Règle | Détail |
|---|---|
| Image immuable et étiquetée | Jamais `latest` |
| Migrations avant démarrage | Étape distincte, bloquante |
| Sonde de démarrage | L'API ne prend du trafic qu'une fois le modèle chargé |
| Retour arrière en une commande | Étiquette d'image précédente |
| Aucun déploiement le vendredi | Règle de bon sens |

## Sauvegarde

| Élément | Fréquence | Conservation |
|---|---|---|
| Base SOLIDA | Quotidienne | 30 jours |
| MinIO — fiches | Continue (versionnage) | Illimitée |
| MLflow | Quotidienne | 90 jours |
| CORE-SIM | Aucune | Se régénère |

**Une sauvegarde non testée n'est pas une sauvegarde.** Restauration vérifiée une fois par mois.

## Reprise après incident

| Scénario | Objectif de reprise | Procédure |
|---|---|---|
| Base SOLIDA corrompue | 4 h | Restauration de la dernière sauvegarde |
| Modèle indisponible | 5 min | Retour à la version précédente |
| MinIO indisponible | Immédiat | Mode dégradé, PDF non archivés |
| CORE-SIM indisponible | 1 h | Le scoring continue sur le feature store |

Le dernier point est un bénéfice de l'architecture batch : même si le SI de l'IMF tombe, SOLIDA
continue de scorer sur les données consolidées de la nuit. À souligner en démonstration.

## Périmètre hackathon

P0 : sonde de santé et journalisation. P2 : le reste.

Ce qui compte devant le jury n'est pas d'avoir tout implémenté, mais de pouvoir répondre
précisément à « comment surveillez-vous ce système en production ? ». Ce document est cette
réponse.
