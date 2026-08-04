# CORE-SIM — schéma de la base simulée

Le schéma détaillé, avec toutes les colonnes et les proportions de génération, se trouve dans
`00-schema-a-valider-par-praticien.md`. Ce fichier-ci en donne la vue d'ingénierie.

## Principes

1. **CORE-SIM imite un système de gestion réel.** Il n'est pas conçu pour arranger notre modèle.
   Si une donnée est difficile à obtenir dans la vraie vie, elle doit être difficile ici aussi.
2. **Lecture seule pour SOLIDA.** Utilisateur `solida_lecteur`, `GRANT SELECT` uniquement.
3. **Reproductible.** Une graine fixe produit exactement la même base.
4. **Paramétré.** Toutes les valeurs numériques sont dans un YAML, aucune dans le code.

## Tables

| Famille | Tables |
|---|---|
| Référentiels | `agence`, `agent_credit`, `produit_credit` |
| Sociétaires | `societaire`, `compte_epargne`, `mouvement_epargne` |
| Solidaire (segment) | `groupe_caution`, `appartenance_groupe`, `garantie` |
| Crédit | `demande_credit`, `credit`, `echeance`, `remboursement` |

## Conventions

| Aspect | Règle |
|---|---|
| Clés primaires | Texte préfixé : `SOC-000123`, `GRP-0042`, `CRD-004512` — lisibles en démonstration |
| Montants | `BIGINT`, en FCFA, jamais de décimal |
| Dates | `DATE` pour les événements métier, `TIMESTAMPTZ` pour les horodatages système |
| Énumérations | `TEXT` avec contrainte `CHECK`, pas de type `ENUM` PostgreSQL (migrations pénibles) |
| Valeurs manquantes | `NULL` explicite, jamais `0` ni chaîne vide |
| Suppression | Aucune. Un statut, jamais un `DELETE` |

## Index nécessaires

| Table | Index | Motif |
|---|---|---|
| `societaire` | `nom_complet` avec `pg_trgm` (GIN) | Recherche tolérante à l'orthographe |
| `societaire` | `numero_membre` unique | Recherche exacte |
| `mouvement_epargne` | `(compte_id, date_operation)` | Agrégation par fenêtre |
| `credit` | `(societaire_id, date_deblocage)` | Historique |
| `echeance` | `(credit_id, date_echeance_prevue)` | Calcul des retards |
| `garantie` | `garant_societaire_id`, `beneficiaire_societaire_id` | Distinction épargne nantie / caution GIE |
| `appartenance_groupe` | `(groupe_id, date_entree, date_sortie)` | Historique de groupe à date |

L'extension `pg_trgm` est **obligatoire** : sans elle, la recherche par nom ne tolère aucune
approximation, ce qui est rédhibitoire pour des noms togolais dont l'orthographe varie.

## Contrôles de cohérence obligatoires (module A7)

Le générateur n'est considéré comme correct que si ces contrôles passent.

| Contrôle | Attendu |
|---|---|
| Aucune garantie ne pointe vers un sociétaire inexistant | 0 violation |
| Aucun crédit sans demande associée | 0 |
| Somme des remboursements ≤ total dû par crédit | 0 dépassement |
| Aucune date de remboursement antérieure au déblocage | 0 |
| Aucun sociétaire membre de deux groupes simultanément | 0, sauf si le praticien indique le contraire |
| Taux de défaut global | dans ±1 point de la cible du YAML |
| Part de primo-emprunteurs | dans ±3 points de la cible |
| Distribution des montants | médiane dans ±10 % de la cible |
| Aucun sociétaire ne se porte garant de lui-même | 0 |
| Cohérence `numero_cycle` avec le nombre de crédits antérieurs | 0 écart |

Un rapport de conformité est produit à chaque génération et versionné avec la graine.
