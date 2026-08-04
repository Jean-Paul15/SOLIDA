# Architecture de l'API

## Cadre

FastAPI, Python 3.12, Pydantic v2, SQLAlchemy 2 en style impératif, Alembic pour les migrations,
Uvicorn derrière un reverse proxy.

## Rôle de la couche HTTP

La couche HTTP est **mince**. Elle fait quatre choses et rien d'autre :

1. Valider l'entrée (Pydantic)
2. Résoudre les dépendances (utilisateur courant, cas d'usage)
3. Appeler **un seul** cas d'usage
4. Traduire le résultat ou l'exception en réponse

**Aucune logique métier dans un routeur.** Un routeur de plus de 20 lignes est suspect. Si une
condition métier apparaît dans un `if` du routeur, elle est au mauvais endroit.

## Organisation

```
adapters/http/
├── routeurs/
│   ├── auth.py
│   ├── societaires.py
│   ├── scoring.py
│   ├── registre.py
│   ├── parametrage.py
│   └── sante.py
├── schemas/          Pydantic — entrée et sortie HTTP uniquement
├── dependances.py    utilisateur courant, cas d'usage, session
└── erreurs.py        exception métier → réponse HTTP
```

**Les schémas Pydantic ne sont pas les entités du domaine.** Ce sont des objets de transport.
La traduction est explicite. Cette séparation permet de faire évoluer l'API sans toucher au
domaine, et inversement.

## Gestion des erreurs

Un gestionnaire central traduit les exceptions métier :

| Exception | Code | Message affiché |
|---|---|---|
| `SocietaireIntrouvable` | 404 | « Ce sociétaire n'existe pas dans le système. » |
| `DonneesInsuffisantes` | 422 | « Les données disponibles ne permettent pas de calculer un score. » |
| `ModeleIndisponible` | 503 | « Le calcul est momentanément indisponible. Réessayez dans un instant. » |
| `GrilleInvalide` | 400 | « Les seuils configurés sont incohérents. » |
| `AccesRefuse` | 403 | « Vous n'avez pas les droits nécessaires pour cette action. » |
| `InvariantScoreViole` | 500 | « Une incohérence a été détectée dans le calcul. Décision non rendue. » |

**Format uniforme :**

```json
{
  "code": "DONNEES_INSUFFISANTES",
  "message": "Les données disponibles ne permettent pas de calculer un score.",
  "details": { "champs_manquants": ["revenu_mensuel_declare"] }
}
```

`message` est en français et destiné à l'agent. `details` est destiné au développeur.
**Aucune trace d'exception n'est renvoyée au client.**

## Injection de dépendances

Les cas d'usage sont construits par un conteneur au démarrage et injectés par `Depends`. Aucun
cas d'usage n'instancie lui-même ses dépendances.

Bénéfice concret : en test, on remplace `LecteurCoreSim` par une doublure sans lancer PostgreSQL.

## Performance

| Cible | Valeur |
|---|---|
| `POST /scoring` | p95 < 800 ms |
| `GET /societaires/recherche` | p95 < 150 ms |
| `GET /societaires/{id}/dossier` | p95 < 400 ms |

Le chemin de scoring ne touche **jamais** CORE-SIM. C'est ce qui rend la cible atteignable.

Le modèle est chargé **une fois** au démarrage et conservé en mémoire. Un chargement par requête
multiplierait la latence par vingt.

## Journalisation

Journal structuré en JSON, un identifiant de corrélation par requête, propagé jusqu'au batch.

**Jamais journalisés :** mot de passe, jeton, nom complet de sociétaire, montant associé à un
identifiant nominatif. Les identifiants opaques suffisent au diagnostic.

## Versionnage

Préfixe `/api/v1`. Une rupture de contrat crée `/api/v2`, elle ne modifie pas `/api/v1`.
Pendant le hackathon, une seule version.
