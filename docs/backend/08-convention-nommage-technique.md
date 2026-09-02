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

## Routeurs et authentification

Les routeurs FastAPI restent dans `infrastructure/routers/` : ils dépendent du framework,
de l’authentification et des fabriques de cas d’usage, donc ne sont pas des adaptateurs purs.
Les dépendances FastAPI (`current_active_user`, `require_role`, `client_ip_address`) vivent dans
`infrastructure/auth/dependencies.py` avec leur implémentation de session. Ainsi, aucun adaptateur
ne dépend de l’infrastructure et la composition de l’application reste directe.

## Autres décisions

- Tous les routeurs HTTP sont regroupés dans `infrastructure/routers/`.
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
