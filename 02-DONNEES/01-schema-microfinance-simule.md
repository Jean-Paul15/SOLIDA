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

**Noms réels (ADR-019, le générateur exécutable fait loi) :** `societaires`, `comptes_epargne`,
`mouvements_epargne`, `groupes_gie`, `appartenances_gie`, `garanties`, `credits`, `choc_secteur`.
Le générateur fusionne demande/échéancier/remboursement dans `credits` (colonnes `defaut` : 1 en
souffrance / 0 solde / -1 en cours, `statut`, `jours_retard_max`), pas trois tables séparées.

| Famille | Tables |
|---|---|
| Référentiels | *(à couvrir par le générateur — non présent dans la version actuelle)*. Taux d'intérêt observé dans `config/config.yaml` du générateur : `taux_interet_annuel: 0,16` dégressif (pratique FUCEC) — valeur de travail à confirmer par une vraie table de taux produit, absente par ailleurs de toute documentation SOLIDA-FOUNDATION. |
| Sociétaires | `societaires`, `comptes_epargne`, `mouvements_epargne` |
| Solidaire (segment) | `groupes_gie`, `appartenances_gie`, `garanties` |
| Crédit | `credits` (demande + échéancier + remboursement fusionnés) |
| Sectoriel | `choc_secteur` |

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
| `societaires` | `nom_complet` avec `pg_trgm` (GIN) | Recherche tolérante à l'orthographe |
| `societaires` | `numero_membre` unique | Recherche exacte |
| `mouvements_epargne` | `(compte_id, date_operation)` | Agrégation par fenêtre |
| `credits` | `(societaire_id, date_deblocage)` | Historique et calcul des retards (échéancier fusionné) |
| `garanties` | `garant_societaire_id`, `beneficiaire_societaire_id` | Distinction épargne nantie / caution GIE |
| `appartenances_gie` | `(groupe_id, date_entree, date_sortie)` | Historique de groupe à date |

L'extension `pg_trgm` est **obligatoire** : sans elle, la recherche par nom ne tolère aucune
approximation, ce qui est rédhibitoire pour des noms togolais dont l'orthographe varie.

## Contrôles de cohérence obligatoires (module A7)

Le générateur n'est considéré comme correct que si ces contrôles passent.

| Contrôle | Attendu |
|---|---|
| Aucune garantie ne pointe vers un sociétaire inexistant | 0 violation |
| Aucun crédit sans sociétaire associé | 0 |
| Capital remboursé ≤ montant octroyé par crédit | 0 dépassement |
| Aucune date de remboursement antérieure au déblocage | 0 |
| Aucun sociétaire membre de deux groupes simultanément | 0, sauf si le praticien indique le contraire |
| Taux de défaut global | dans ±1 point de la cible du YAML |
| Part de primo-emprunteurs | dans ±3 points de la cible |
| Distribution des montants | médiane dans ±10 % de la cible |
| Aucun sociétaire ne se porte garant de lui-même | 0 |
| Cohérence `numero_cycle` avec le nombre de crédits antérieurs | 0 écart |

Un rapport de conformité est produit à chaque génération et versionné avec la graine.
