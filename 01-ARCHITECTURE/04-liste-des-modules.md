# Liste des modules

Chaque module a **une responsabilité, une entrée, une sortie et un propriétaire unique**.
Deux personnes ne travaillent jamais dans le même module en même temps.

Colonne **P** : priorité selon `00-CONTEXTE/03-perimetre-hackathon.md`.

---

## Bloc A — Simulateur

| # | Module | Responsabilité | Entrée | Sortie | P |
|---|---|---|---|---|---|
| A1 | `simulateur.config` | Tous les paramètres de génération, externalisés | Fichier YAML | Objet de configuration validé | P0 |
| A2 | `simulateur.entites` | Génération des sociétaires, agences, agents, produits | Config + graine | Tables de référence | P0 |
| A3 | `simulateur.solidaire` | Groupes de caution (segment groupement), appartenances, garanties | Sociétaires | Tables du segment solidaire | P0 |
| A4 | `simulateur.epargne` | Comptes et mouvements d'épargne | Sociétaires | Tables épargne | P0 |
| A5 | `simulateur.credit` | Demandes, crédits, échéanciers, remboursements, défauts | Tout ce qui précède | Tables crédit | P0 |
| A6 | `simulateur.chargement` | Écriture dans PostgreSQL CORE-SIM | Tables | Base peuplée | P0 |
| A7 | `simulateur.controle` | Contrôles de cohérence post-génération | Base | Rapport de conformité | P0 |

**Règle A :** la mécanique de génération ne contient aucune valeur numérique. Tout vient de A1.
Le retour du praticien IMF ne doit modifier que le YAML.

---

## Bloc B — Domaine SOLIDA

| # | Module | Responsabilité | P |
|---|---|---|---|
| B1 | `domain.entities` | Entités métier immuables | P0 |
| B2 | `domain.values` | `Montant`, `Score`, `Tranche`, `ProbabiliteDefaut`, `PointsVariable` | P0 |
| B3 | `domain.rules.scorecard` | PD → log-odds → score, décomposition en points | P0 |
| B4 | `domain.rules.grille` | Score → tranche → décision + plafond | P0 |
| B5 | `domain.rules.cascade` | Choix socle / enrichi, détection démarrage à froid | P0 |
| B6 | `domain.rules.progressif` | Plafond selon le cycle et l'historique | P1 |
| B7 | `domain.ports` | Toutes les interfaces abstraites | P0 |

**Règle B :** ce bloc n'importe rien d'externe. Il est testé à 100 %.

---

## Bloc C — Données et features

| # | Module | Responsabilité | Entrée | Sortie | P |
|---|---|---|---|---|---|
| C1 | `adapters.core_sim` | Lecture seule de CORE-SIM, mapping vers entités | SQL | Entités du domaine | P0 |
| C2 | `features.individuel` | Variables du socle | Entités | `FeaturesIndividuelles` | P0 |
| C3 | `features.epargne` | Trajectoire d'épargne dynamique (tendance, régularité, effort) | Comptes + mouvements | `FeaturesIndividuelles` (bloc épargne) | P0 |
| C4 | `features.solidaire` | Agrégats du segment de groupe (SQL, pas de graphe) | Groupes + garanties | `FeaturesSolidaires` | P1 |
| C5 | `adapters.feature_store` | Persistance et lecture du feature store | Features | Tables SOLIDA | P0 |
| C6 | `data.validation` | Contrôle de schéma et de qualité en entrée | Données brutes | Rapport + rejet | P1 |

**Règle C :** C2, C3 et C4 sont des fonctions pures `entités → features`. Elles ne lisent pas la
base elles-mêmes ; on leur passe les données. C'est ce qui permet de les tester et de les rejouer.
C2 et C3 alimentent ensemble `FeaturesIndividuelles` (voir `01-ARCHITECTURE/05`) ; C3 porte
spécifiquement le bloc trajectoire d'épargne, qui est le signal central du socle.

---

## Bloc D — Modèle

| # | Module | Responsabilité | P |
|---|---|---|---|
| D1 | `ml.dataset` | Construction de la matrice, découpage temporel, définition de la cible | P0 |
| D2 | `ml.entrainement` | Entraînement EBM socle et enrichi, logistique de référence | P0 |
| D3 | `ml.calibration` | Vérification et correction de la calibration | P0 |
| D4 | `ml.evaluation` | AUC, Gini, KS, courbe de calibration, comparatif | P0 |
| D5 | `ml.explication` | Extraction des contributions par variable | P0 |
| D6 | `ml.registre` | Versionnage, MLflow, chargement du modèle actif | P1 |
| D7 | `ml.derive` | PSI, dérive des variables et de la cible | P2 |

---

## Bloc E — Application et API

| # | Module | Responsabilité | P |
|---|---|---|---|
| E1 | `use_cases.rechercher_societaire` | Recherche par nom, retour d'une liste courte | P0 |
| E2 | `use_cases.consulter_dossier` | Vue 360° d'un sociétaire | P0 |
| E3 | `use_cases.scorer_demande` | Orchestration complète du scoring : score, grille, moteur de crédit progressif, conditions de réexamen (`domain/rules/progressif.py`) | P0 |
| E4 | `use_cases.generer_fiche` | Fiche de justification et PDF | P1 |
| E5 | `use_cases.consulter_groupe` | Liste des membres du groupe de caution d'un sociétaire (segment groupement) | P1 |
| E6 | `use_cases.parametrer_grille` | Modification des seuils par le superviseur | P2 |
| E7 | `adapters.http` | Routeurs FastAPI, schémas d'entrée/sortie, dépendances | P0 |
| E8 | `auth` | Authentification, rôles, session | P0 |
| E9 | `audit` | Journal des décisions | P1 |

---

## Bloc F — Batch

| # | Module | Responsabilité | P |
|---|---|---|---|
| F1 | `batch.rafraichir_features` | Recalcul complet du feature store | P0 |
| F2 | `batch.calculer_agregats_solidaires` | Calcul des agrégats du segment de groupe (SQL, pas de graphe) | P1 |
| F3 | `batch.orchestration` | Enchaînement, journalisation, reprise sur erreur | P1 |

---

## Bloc G — Front

| # | Module | Responsabilité | P |
|---|---|---|---|
| G1 | `ui/design-system` | Jetons, primitives, thème | P0 |
| G2 | `services/api` | Client HTTP typé | P0 |
| G3 | `features/recherche` | Recherche de sociétaire | P0 |
| G4 | `features/dossier` | Fiche 360° | P0 |
| G5 | `features/demande` | Saisie de la demande | P0 |
| G6 | `features/resultat` | Restitution du score | P0 |
| G7 | `features/justification` | Fiche et export PDF | P1 |
| G8 | `features/groupe` | Tableau du groupe de caution (segment groupement) | P1 |
| G9 | `features/registre` | Registre des décisions | P2 |
| G10 | `features/parametrage` | Grille et supervision modèle | P2 |
| G11 | `auth` | Connexion, session, garde de routes | P0 |

---

## Bloc H — Infrastructure

| # | Module | Responsabilité | P |
|---|---|---|---|
| H1 | `docker/` | Compose, images, volumes | P0 |
| H2 | `migrations/` | Schéma SOLIDA versionné | P0 |
| H3 | `observabilite/` | Journalisation structurée, métriques, traces | P2 |
| H4 | `ci/` | Hooks, pipeline, qualité | P1 |

---

## Graphe de dépendances entre blocs

```
A (simulateur)  ──►  CORE-SIM  ──►  C1
                                     │
B (domaine) ◄────────────────────────┤
   │                                 ▼
   ├──► C2, C3, C4 ──► C5 ──► D1 ──► D2 ──► D3 ──► D6
   │                                          │
   └──► E3 ◄──────────────────────────────────┘
         │
         └──► E7 ──► G2 ──► G3..G10
```

**Chemin critique du hackathon :** A → C1 → C2 → D1 → D2 → B3/B4 → E3 → E7 → G6.
Tout ce qui n'est pas sur ce chemin est secondaire tant que le chemin n'est pas complet.
