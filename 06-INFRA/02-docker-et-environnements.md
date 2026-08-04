# Docker et environnements

## Principes

| Principe | Détail |
|---|---|
| Une commande pour tout démarrer | `docker compose up` doit suffire |
| Aucune donnée dans une image | Les données viennent de volumes ou du générateur |
| Aucun secret dans une image | Variables d'environnement uniquement |
| Images minces | Multi-étapes, base `slim` |
| Démarrage ordonné | `depends_on` avec `healthcheck`, pas d'attente arbitraire |

Le dernier point évite le classique « ça marche chez moi » du matin du jour 1 : l'API qui démarre
avant que PostgreSQL n'accepte les connexions.

## Environnements

| Environnement | Usage | Particularités |
|---|---|---|
| `local` | Développement | Rechargement à chaud, journaux verbeux, CORE-SIM peuplé |
| `demo` | Hackathon | Données figées et vérifiées, journaux normaux, aucune donnée sensible |
| `production` | Après hackathon | Journaux structurés, métriques, sauvegardes |

**L'environnement `demo` est le plus important pour le hackathon.** Il doit être reproductible en
une commande et contenir un jeu de cas préparé pour la démonstration, dont le cas « démarrage à
froid ». On ne cherche pas un bon dossier devant le jury, on l'a préparé.

## Configuration

| Règle | Détail |
|---|---|
| Toute configuration par variable d'environnement | Aucune valeur en dur |
| `.env.example` versionné et complet | Sert de documentation |
| `.env` jamais versionné | Bloqué par `.gitignore` et par un hook |
| Validation au démarrage | Pydantic Settings ; une variable manquante empêche le démarrage |
| Pas de valeur par défaut sur un secret | Un secret par défaut finit en production |

**L'échec au démarrage est volontaire.** Un service qui démarre avec une configuration incomplète
échouera plus tard, de manière obscure.

## Volumes

| Volume | Contenu | Persistant |
|---|---|---|
| `pgdata-coresim` | Base simulée | Non — se régénère |
| `pgdata-solida` | Base SOLIDA | Oui |
| `miniodata` | Objets | Oui |
| `mlruns` | Expériences MLflow | Oui |

CORE-SIM est explicitement non persistant : sa régénération à partir d'une graine est plus fiable
qu'une sauvegarde, et cela force à maintenir le générateur en état de marche.

## Sauvegarde

Pendant le hackathon : export `pg_dump` de la base SOLIDA à la fin de chaque journée, sur deux
supports distincts. Ce n'est pas de la paranoïa ; perdre les modèles entraînés et les décisions à
la fin du jour 2 coûterait la compétition.

## Réseau

Un réseau Docker interne. Seuls `front` et `api` sont exposés à l'extérieur. PostgreSQL, MinIO et
MLflow ne sont accessibles que depuis le réseau interne, même en local.
