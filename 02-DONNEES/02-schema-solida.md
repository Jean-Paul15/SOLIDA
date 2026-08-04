# Base SOLIDA — schéma

Base distincte de CORE-SIM. Contient uniquement ce que **nous** produisons.

## Tables

### Copie du segment solidaire

| Table | Contenu |
|---|---|
| `groupe_caution` | Copie du groupe (segment GIE), voir `01-ARCHITECTURE/07` |
| `appartenance_groupe` | `societaire_id`, `groupe_id`, `date_entree`, `date_sortie`, `role` |
| `garantie` | `garant_societaire_id` (nullable), `beneficiaire_societaire_id`, `type_garantie`, `date_engagement`, `garantie_appelee` |

Copiées depuis CORE-SIM par le batch, avec leurs dates de validité, ce qui permet de recalculer les
agrégats de groupe **à une date passée** — indispensable pour éviter la fuite temporelle à
l'entraînement. Aucune table de nœuds/arêtes génériques : ce sont des tables métier ordinaires.

### Feature store

| Table | Contenu |
|---|---|
| `feature_individuelle` | `societaire_id`, `date_reference`, une colonne par variable (dont la trajectoire d'épargne), `date_calcul` |
| `feature_solidaire` | `societaire_id`, `date_reference`, une colonne par variable, `date_calcul` — `null` hors segment de groupe |

Clé : `(societaire_id, date_reference)`. Historisé, jamais écrasé. Permet le rejeu.

### Index de recherche

| Table | Contenu |
|---|---|
| `index_societaire` | `societaire_id`, `nom_normalise`, `numero_membre`, `agence`, `zone`, `statut`, `a_credit_en_cours` |

Rafraîchi par le batch. Sert la recherche du guichet **sans toucher CORE-SIM**.

### Modèles

| Table | Contenu |
|---|---|
| `modele` | `modele_id`, `type` (socle/enrichi/reference), `version`, `chemin_artefact`, `metriques` (JSONB), `date_entrainement`, `actif` |
| `grille_decision` | `version_grille`, `seuils` (JSONB), `pdo`, `score_reference`, `odds_reference`, `date_activation`, `auteur` |

### Décisions et audit

| Table | Contenu |
|---|---|
| `decision_scoring` | `decision_id`, `societaire_id`, `agent_id`, `entree` (JSONB), `features_utilisees` (JSONB), `probabilite`, `score`, `tranche`, `montant_recommande`, `mode_calcul`, `decomposition` (JSONB), `version_modele`, `version_grille`, `horodatage` |
| `decision_finale` | `decision_id`, `decision_agent`, `montant_accorde`, `motif_ecart`, `horodatage` |
| `fiche_generee` | `fiche_id`, `decision_id`, `cle_minio`, `horodatage` |
| `journal_audit` | `evenement_id`, `type`, `acteur_id`, `objet`, `details` (JSONB), `horodatage`, `adresse_ip` |

**`decision_scoring` est la table la plus importante du système.** Elle contient tout ce qu'il faut
pour rejouer une décision à l'identique des années plus tard : les entrées, les features telles
qu'elles étaient, le modèle, la grille, le résultat. Sans elle, ni audit, ni recalibrage, ni
défense d'une décision.

### Utilisateurs

| Table | Contenu |
|---|---|
| `utilisateur` | `utilisateur_id`, `identifiant`, `empreinte_mot_de_passe`, `nom_complet`, `role`, `agence_id`, `actif`, `date_creation` |
| `session` | `session_id`, `utilisateur_id`, `empreinte_jeton`, `expiration`, `revoquee` |

## Règles

| Règle | Motif |
|---|---|
| Aucune clé étrangère vers CORE-SIM | Les deux bases sont indépendantes |
| Les identifiants de CORE-SIM sont stockés comme texte opaque | Ils identifient, ils ne contraignent pas |
| `decision_scoring` est en **insertion seule** | Une décision ne se modifie pas |
| Migrations versionnées (Alembic) | Reproductibilité |
| Les JSONB sont validés à l'écriture | Un JSONB non validé devient vite un dépotoir |
