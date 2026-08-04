# Postgres et simulateur CORE-SIM

## Services

| Service | Rôle | Port publié |
|---|---|---|
| `postgres-coresim` | Base simulée, non persistante | aucun (réseau interne uniquement) |
| `postgres-solida` | Base SOLIDA, persistante (`pgdata_solida`) | aucun (réseau interne uniquement) |
| `coresim-seed` | Génère et charge les données CORE-SIM (profil `tools`, exécution manuelle) | — |

## Démarrer

```
docker compose up -d postgres-coresim postgres-solida
docker compose run --rm coresim-seed
```

`coresim-seed` construit `./simulateur` (Dockerfile dédié, `requirements.txt` épinglé),
lance `pipeline.py` puis `charger_postgres.py`. Résultat vérifié : 12 000 sociétaires, ~8 100
crédits, taux de souffrance et part d'emprunteurs conformes aux cibles du générateur.

## Garde-fou vérifié

Le rôle `solida_lecteur` (`infra/postgres/coresim-init.sh`) peut lire `coresim` mais pas y écrire —
testé avec un `INSERT` réel, refusé (`permission denied`). C'est le garde-fou central de
`06-INFRA/03-postgresql.md`.

## Sécurité des conteneurs Postgres

`cap_drop: ALL` casse l'entrypoint officiel de l'image Postgres (a besoin de `CAP_CHOWN`/
`CAP_SETUID` pour démarrer root puis basculer sur l'utilisateur `postgres`) — non appliqué ici,
contrairement au service `front`. Isolation assurée autrement : aucun port publié vers l'hôte,
réseau Docker interne dédié, rôles applicatifs à privilège minimal.

## Écart de schéma

Voir ADR-019 (`00-CONTEXTE/04-journal-de-decisions.md`) : les noms de tables réels
(`societaires`, `comptes_epargne`, `groupes_gie`, `credits`, `garanties`, `mouvements_epargne`,
`choc_secteur`) diffèrent de `02-DONNEES/01`, corrigé en conséquence.
