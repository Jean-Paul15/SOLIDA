# Clean Architecture appliquée à SOLIDA

## La règle de dépendance

Les dépendances pointent **toujours vers l'intérieur**. Une couche ne connaît jamais celle qui
l'englobe.

```
        ┌─────────────────────────────────────────────┐
        │  INFRASTRUCTURE                             │
        │  PostgreSQL · MinIO · MLflow · FastAPI      │
        │  Next.js · Prometheus · EBM                  │
        │   ┌───────────────────────────────────────┐ │
        │   │  ADAPTATEURS                          │ │
        │   │  Dépôts · Client CORE-SIM · Rendu PDF │ │
        │   │  Contrôleurs HTTP · Jobs batch        │ │
        │   │   ┌─────────────────────────────────┐ │ │
        │   │   │  APPLICATION (cas d'usage)      │ │ │
        │   │   │  ScorerUneDemande               │ │ │
        │   │   │  CalculerAgregatsSolidaires      │ │ │
        │   │   │  RafraichirLeFeatureStore       │ │ │
        │   │   │   ┌───────────────────────────┐ │ │ │
        │   │   │   │  DOMAINE                  │ │ │ │
        │   │   │   │  Entités · Règles · Ports │ │ │ │
        │   │   │   │  Score · Grille · Cascade │ │ │ │
        │   │   │   └───────────────────────────┘ │ │ │
        │   │   └─────────────────────────────────┘ │ │
        │   └───────────────────────────────────────┘ │
        └─────────────────────────────────────────────┘
```

## Ce que contient chaque couche

### Domaine — `solida/domain/`

Le cœur. Aucun import de librairie externe autre que la bibliothèque standard et Pydantic pour la
validation de valeur.

- **Entités** : `Societaire`, `DemandeCredit`, `GroupeCaution`, `Garantie`, `Credit`
- **Objets valeur** : `Montant` (FCFA, entier, jamais un flottant), `Score`, `TrancheDecision`,
  `ProbabiliteDefaut`, `PointsVariable`
- **Règles pures** : transformation PD → score, décomposition en points, grille de décision,
  cascade, plafond progressif
- **Ports** (interfaces abstraites) : `LecteurCoreSim`, `FeatureStore`, `ModeleScoring`,
  `Explicateur`, `GenerateurFiche`, `JournalAudit`, `RegistreModeles`

Test : ces fichiers doivent s'exécuter dans un interpréteur nu, sans base ni réseau.

### Application — `solida/application/`

Orchestration des cas d'usage. Connaît le domaine, ignore l'infrastructure.

Un cas d'usage = une classe, une méthode publique `executer()`, des dépendances injectées par
constructeur sous forme de ports.

### Adaptateurs — `solida/adapters/`

Implémentations concrètes des ports. C'est ici, et seulement ici, qu'on trouve du SQL, du HTTP,
du S3, du scikit-learn.

### Infrastructure — `solida/infrastructure/`

Câblage : composition des dépendances, configuration, création de l'application FastAPI,
connexions, journalisation, métriques.

## Arborescence de référence

```
backend/
├── solida/
│   ├── domain/
│   │   ├── entities/           societaire.py, demande.py, groupe.py, credit.py
│   │   ├── values/             montant.py, score.py, tranche.py
│   │   ├── rules/              scorecard.py, grille.py, cascade.py, progressif.py
│   │   └── ports/              core_sim.py, feature_store.py, modele.py, audit.py
│   ├── application/
│   │   └── use_cases/          scorer_demande.py, calculer_agregats_solidaires.py,
│   │                           rafraichir_features.py, generer_fiche.py
│   ├── adapters/
│   │   ├── core_sim/           lecteur_postgres.py
│   │   ├── persistence/        depots_postgres.py, modeles_sqlalchemy.py
│   │   ├── solidaire/          agregats_groupe.py, requetes_sql.py
│   │   ├── ml/                 modele_ebm.py, calibration.py, registre_mlflow.py
│   │   ├── storage/            client_minio.py
│   │   ├── pdf/                generateur_fiche.py
│   │   └── http/               routeurs/, schemas/, dependances.py
│   ├── infrastructure/         config.py, conteneur.py, journalisation.py, metriques.py
│   └── batch/                  jobs/, planificateur.py
└── tests/
    ├── domain/                 rapides, sans dépendance
    ├── application/            avec doublures
    └── integration/            avec conteneurs
```

## Interdits vérifiables

Ces règles sont contrôlées par le linter (`import-linter`) et par un hook Git.

| Depuis | Ne peut pas importer |
|---|---|
| `domain/` | `application/`, `adapters/`, `infrastructure/`, toute librairie tierce hors stdlib et Pydantic |
| `application/` | `adapters/`, `infrastructure/` |
| `adapters/` | `infrastructure/` |

## Frontière côté front

Le front applique le même esprit avec trois couches :

| Couche | Contenu | Connaît |
|---|---|---|
| `domain/` | Types métier, formatage FCFA, calcul de tranche pour l'affichage | rien |
| `services/` | Client HTTP typé, mapping DTO → type métier | `domain` |
| `components/` + `app/` | Rendu et interaction | `domain`, `services` |

Un composant ne fait jamais d'appel `fetch` direct. Il consomme un service.
