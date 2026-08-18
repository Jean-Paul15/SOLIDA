# Convention de nommage technique (refactor SOLID / anglicisation)

## Décision

Le vocabulaire métier reste en français (`societaire`, `groupe_caution`,
`score_octroi`, `cautionnaire`, `dossier`, `credit`, `epargne`...). Le
vocabulaire technique générique (rôle d'une classe dans l'architecture, pas
concept métier) passe en anglais. Les deux ne se mélangent jamais dans un
même identifiant.

Le problème corrigé : le rôle technique était placé en tête à la française
(`DepotDecisions`, `LecteurCoreSim`) plutôt qu'en position finale, comme le
veut l'anglais idiomatique (`DecisionRepository`, `CoreSimReader`).

## Ports (`domain/ports/`)

`<Concept métier ou système, inchangé> + <Rôle technique traduit, en dernier>`

| Ancien | Nouveau |
|---|---|
| `DepotDecisions` | `DecisionRepository` |
| `DepotGrille` | `GrilleRepository` |
| `DepotFiches` | `FicheRepository` |
| `DepotFichesArchivees` | `FicheArchiveeRepository` |
| `LecteurCoreSim` | `CoreSimReader` |
| `JournalAudit` | `AuditLog` |
| `GenerateurFichePdf` | `FichePdfGenerator` |
| `ModeleScoring` | `ScoringModel` |
| `FeatureStore` | inchangé (déjà conforme) |

## Adaptateurs concrets

Technologie en préfixe, rôle en suffixe : `DepotDecisionsSql` →
`SqlDecisionRepository`, `LecteurCoreSimPostgres` → `PostgresCoreSimReader`,
`GenerateurFichePdfWeasyPrint` → `WeasyPrintFichePdfGenerator`, etc. Fichier
renommé en miroir (`decisions_sql.py` → `decision_repository_sql.py`).

## Ce qui ne change pas

Les noms de méthodes (`charger_societaire`, `rechercher_societaires`,
`enregistrer`...) restent en français : ce sont des verbes métier, pas des
rôles techniques génériques. Les champs de dataclass qui portent un port
(`lecteur`, `depot_grille`...) sont renommés en miroir exact du type
(`reader`, `grille_repository`), dans le même commit que le port.

## Frontière d'authentification adapters ↔ infrastructure

Les 6 routeurs métier (`auth`, `societaires`, `scoring`, `registre`,
`parametrage`, `produits`) migrent de `infrastructure/routeurs/` vers
`adapters/http/routeurs/` (aligné sur `health.py`, seul routeur déjà bien
placé). Comme le contrat `import-linter` interdit à `adapters` d'importer
`infrastructure`, l'authentification FastAPI traverse cette frontière via le
pattern `dependency_overrides` :

- `adapters/http/auth_dependencies.py` déclare des fonctions stub stables
  (`current_active_user`, une fonction par rôle) que les routeurs importent.
- `infrastructure/application_fastapi.py` (composition root) enregistre les
  implémentations réelles via `app.dependency_overrides[...]` au moment de
  l'assemblage de l'application — seul point qui connaît à la fois les stubs
  et `infrastructure/auth.py`.

## Autres décisions

- `adapters/http/routeurs/health.py` reste la référence de placement.
- `adapters/solidaire/` (dossier vide, jamais complété) : supprimé.
- `adapters/libelles_variables.py` déplacé vers `adapters/http/` (seul
  consommateur : les mappers HTTP).
- `infrastructure/journalisation.py` → `infrastructure/logging.py` ;
  `infrastructure/middleware_journalisation.py` →
  `infrastructure/access_logging_middleware.py` (terme technique générique,
  pas métier).
- `frontend/lib/contracts.ts` : seuls les noms de *types* passent en
  anglais (`ResultatScoring` → `ScoringResult`) ; les champs JSON et les
  types authentiquement métier (`DossierSocietaire`, `SyntheseGroupe`...)
  restent en français.

Détail complet du séquencement en phases : voir le plan de refactor associé
à cette tâche.
