# PostgreSQL

## Deux instances

| Instance | Base | Utilisateurs |
|---|---|---|
| `postgres-coresim` | `coresim` | `coresim_admin` (générateur, lecture/écriture), `solida_lecteur` (**SELECT uniquement**) |
| `postgres-solida` | `solida` | `solida_app` (lecture/écriture), `solida_lecture` (rapports) |

**Le rôle `solida_lecteur` est le garde-fou central de l'architecture.**

```sql
CREATE ROLE solida_lecteur LOGIN PASSWORD '...';
GRANT CONNECT ON DATABASE coresim TO solida_lecteur;
GRANT USAGE ON SCHEMA public TO solida_lecteur;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO solida_lecteur;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO solida_lecteur;
```

Un test d'intégration tente un `INSERT` avec ce rôle et **doit échouer**. Si ce test passe, la
configuration est fausse et la frontière n'existe plus.

## Extensions

| Extension | Base | Usage |
|---|---|---|
| `pg_trgm` | `coresim` | Recherche par nom tolérante à l'orthographe |
| `unaccent` | `coresim` | Insensibilité aux accents |
| `pgcrypto` | `solida` | Génération d'identifiants |

`pg_trgm` et `unaccent` sont **indispensables**. Les noms togolais s'écrivent de plusieurs façons ;
une recherche exacte serait inutilisable en agence.

## Recherche par nom

```sql
CREATE INDEX idx_societaire_nom_trgm
  ON societaire USING GIN (unaccent(lower(nom_complet)) gin_trgm_ops);
```

Requête : combinaison d'une correspondance par préfixe et d'une similarité trigramme, seuil 0,3,
tri par similarité décroissante puis par nom.

En production, la recherche interroge `index_societaire` dans la base SOLIDA, pas CORE-SIM, afin de
ne rien demander au système de l'IMF pendant les heures d'ouverture.

## Migrations

Alembic. Une migration par changement, réversible, jamais modifiée après application.
Nommage : `20260901_1430_ajout_table_decision_scoring.py`.

**Aucune modification manuelle du schéma.** Un `ALTER TABLE` passé à la main en console est
invisible pour les autres et casse l'environnement de tout le monde le lendemain.

## Performance

| Règle | Détail |
|---|---|
| Toute clé étrangère est indexée | PostgreSQL ne le fait pas automatiquement |
| Pas de `SELECT *` en production | Colonnes explicites |
| Écritures du batch par lots | `execute_values`, pas ligne à ligne |
| `EXPLAIN ANALYZE` sur toute requête de plus de 100 ms | Systématique |
| Pool de connexions | Dimensionné, pas de connexion par requête |

## Types

| Concept | Type | Motif |
|---|---|---|
| Montant | `BIGINT` | FCFA entiers |
| Date métier | `DATE` | Pas d'heure sur un événement métier |
| Horodatage système | `TIMESTAMPTZ` | Toujours avec fuseau |
| Identifiant | `TEXT` | Lisible en démonstration |
| Énumération | `TEXT` + `CHECK` | Migrations plus simples qu'avec `ENUM` |
| Structure variable | `JSONB` | Validé à l'écriture |
| Ratio | `NUMERIC(6,4)` | Jamais `float` sur une donnée métier |
