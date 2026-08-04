# Adaptateur CORE-SIM

`solida/adapters/core_sim/lecteur_postgres.py` implémente `LecteurCoreSim` contre le schéma
exécutable réel du générateur (`simulateur/`), pas contre `02-DONNEES/01` littéralement (ADR-019).
Connexion via le rôle `solida_lecteur` (lecture seule, `GRANT SELECT` uniquement) — vérifié contre
la base réelle peuplée par `coresim-seed` (12 000 sociétaires), pas seulement par des doublures.

## Colonnes absentes du générateur, estimées à l'affichage

Le générateur produit des données brutes (montant, durée, statut) mais pas d'échéancier de
remboursement détaillé ni certains champs de présentation. Ces valeurs sont **calculées dans
l'adaptateur**, pas dans le domaine (ce sont des approximations d'affichage, pas des règles
métier) :

| Champ | Absent du générateur | Approximation |
|---|---|---|
| `statut` (actif/inactif/radié) sur `Societaire` | Oui, aucun modèle de churn | `actif` pour tout le monde |
| `capital_restant_du` sur `Credit` | Oui, pas d'échéancier | `solde` → 0. `en_souffrance` → `montant_octroye` en entier (aucune donnée de remboursement partiel n'existe : traiter comme intégralement impayé plutôt que d'appliquer un amortissement qui supposerait, à tort, un remboursement en cours). `en_cours` → amortissement linéaire sur la durée écoulée |
| `nom_groupe` | Oui, seulement un identifiant `GIE-xxxx` | `"Groupement {gie_id}"` |
| `statut` du groupe (actif/dissous/en_difficulté) | Oui | `dissous` si plus aucun membre actif, `en_difficulté` si taux de remboursement < 50 %, sinon `actif` |

## Agrégats de groupe : toujours du point de vue du sociétaire consulté

`charger_groupe(societaire_id)` exclut systématiquement ce sociétaire de `taux_remboursement_groupe`,
`nb_cycles_completes` et `nb_credits_anterieurs_soldes` — la règle de
`03-MODELE/04-cascade-et-cold-start.md` ("hors sociétaire évalué"), appliquée uniformément à
l'affichage (E2, E5) et à la cascade, pas seulement au calcul du score. Deux sociétaires du même
groupe verront donc des chiffres de groupe légèrement différents pour ce champ, ce qui est
intentionnel.

## Variables jamais lues

`sexe` et `statut_matrimonial` existent dans la table `societaires` mais ne sont **jamais**
sélectionnées par cet adaptateur : engagement de non-discrimination
(`03-MODELE/06-ethique-et-non-discrimination.md`), pas seulement absence côté modèle.
