# Persistance et migrations

## Schéma `solida` (Alembic, migration initiale)

Sept tables : `utilisateur`, `access_token` (authentification, voir plus bas), `grille_decision`,
`modele`, `decision_scoring`, `journal_audit`. Vérifié par un cycle complet
`upgrade head` → `downgrade base` → `upgrade head` sur la base réelle, pas seulement en théorie.

Tables volontairement absentes de cette passe (voir `03-decisions-provisoires-a-revoir.md`) :
`decision_finale`, `fiche_generee`, les copies batch du segment solidaire
(`groupe_caution`/`appartenance_groupe`/`garantie`), le feature store historisé, l'index de
recherche dédié. Aucune de ces tables n'est nécessaire tant que la recherche et le calcul de
features lisent CORE-SIM directement.

## `decision_scoring` : garde-fou en base, pas seulement applicatif

Un déclencheur (`decision_scoring_insertion_seule`) empêche toute requête `UPDATE` ou `DELETE` sur
cette table, quel que soit le rôle qui l'exécute — vérifié en base réelle : une décision insérée
ne peut ensuite être ni modifiée ni supprimée, seule une nouvelle insertion est possible. Une
décision de crédit ne se corrige pas rétroactivement, elle se rejoue.

## Grille et progressif : paramétrables en base, pas dans le code

`grille_decision.seuils` (JSONB) porte `marge`, `lgd`, les multiplicateurs de zone, et tous les
paramètres du crédit progressif — y compris `plafond_produit`, le montant que le système ne
recommande jamais de dépasser. Une ligne `v0.1` est semée par la migration avec les valeurs de
départ du prototype de référence. Changer ces valeurs ne demande ni redéploiement ni modification
de code : une nouvelle ligne versionnée dans cette table suffit.

## Authentification : tables FastAPI-Users renommées

`utilisateur` (pas `user`) et `access_token`. Le mixin `SQLAlchemyBaseAccessTokenTableUUID` cible
`"user.id"` en dur dans sa définition de clé étrangère : la colonne `user_id` est redéclarée
explicitement dans notre modèle pour cibler `utilisateur.id`, avec le même type `GUID` que la
bibliothèque utilise pour rester compatible.
