# Cas d'usage et routeurs HTTP

## Endpoints, alignés sur le contrat frontend existant

`GET /api/v1/societaires/recherche`, `GET /api/v1/societaires/{id}/dossier`,
`GET /api/v1/societaires/{id}/groupe`, `POST /api/v1/scoring`, `GET /api/v1/scoring/{id}`,
`GET /api/v1/scoring/{id}/fiche` reprennent exactement les routes déjà appelées par le mock
frontend (`frontend/app/api/v1/**`). `GET /api/v1/registre` et `GET`/`POST /api/v1/parametrage/grille`
sont nouveaux : E7 et E8 lisent aujourd'hui leurs données directement depuis les mocks côté
serveur (aucun appel HTTP existant), ces deux routes n'ont donc aucun contrat frontend gelé à
respecter — leur forme (nommage `snake_case`, `{elements, total}` pour la pagination) suit la
convention déjà posée par `societaires/recherche`, pas une spécification préexistante. E9
(supervision du modèle) a été retiré du périmètre produit, aucun endpoint ne lui correspond.

## Cloisonnement par agence : sur l'agent qui agit, pas sur le sociétaire visé

CORE-SIM et `solida` sont deux bases séparées : impossible de joindre directement
`societaires.caisse_id` depuis une requête sur `decision_scoring`. Deux règles distinctes,
appliquées selon ce qui est consulté :

- **Recherche et dossier d'un sociétaire** (`/societaires/...`) : comparent directement
  `societaires.caisse_id` (même base CORE-SIM) à `utilisateur.agence_id` de l'agent connecté.
- **Décisions déjà prises** (`/scoring/{id}`, `/scoring/{id}/fiche`, `/registre`) : comparent
  l'agence de l'**agent qui a pris la décision** (`decision_scoring.agent_id` → 
  `utilisateur.agence_id`, dénormalisée dans `DecisionEnregistree.agent_agence_id` au moment de
  l'écriture pour éviter une jointure à chaque lecture), pas l'agence du sociétaire concerné.

Chaque vérification est refaite côté serveur (`AccesRefuse` → 403), jamais seulement déduite du
rôle affiché côté frontend.

## `utilisateur.agence_id` doit être un vrai code CORE-SIM

Les comptes de démonstration utilisent `CAI-00`/`CAI-01` (codes réels de `societaires.caisse_id`),
pas un nom de convenance — sinon le cloisonnement ci-dessus ne matche jamais rien. Voir
`04-authentification.md`.

## `ScorerDemande` : features de profil vs. features de la demande

`FeatureStore.lire_individuelles(societaire_id)` ne connaît que le sociétaire, pas le montant ou
la durée demandés. `ratio_endettement`, `ratio_epargne_montant` et `ratio_epargne_revenu` — qui
dépendent de la demande en cours et d'un revenu éventuellement actualisé par l'agent
(`EntreeScoring.actualisation`) — sont donc toujours recalculés dans `scorer_demande` avant
construction du dictionnaire envoyé au modèle et avant persistance. Voir le docstring de
`FeatureStoreCoreSim` pour le détail.

## Persistance JSONB avec psycopg 3 : `bindparams(type_=JSONB)` obligatoire

Un dictionnaire Python n'est pas adapté automatiquement par psycopg 3 dans une requête `text()`
brute (`cannot adapt type 'dict'`) : chaque paramètre JSONB/JSON doit être déclaré explicitement
via `text(...).bindparams(bindparam("champ", type_=JSONB))` avant exécution. Touche
`decisions_sql.py`, `grille_sql.py` et `journal_audit_sql.py` — vérifié par un vrai scoring de
bout en bout contre la base réelle, pas seulement en théorie (l'erreur n'apparaît qu'à l'exécution,
jamais à la vérification de types).

## `decision_scoring.resultat_complementaire`

`decision_scoring` porte déjà `score`, `tranche`, `montant_recommande`, `decomposition`, etc. en
colonnes, mais pas `motif_mode`, `points_de_base`, `plafond_progressif`, `trajectoire_progression`,
`conditions_reexamen` ni `avertissements` — regroupés dans cette colonne JSONB ajoutée par une
migration dédiée (`f7e6a07b7371`). Nécessaire parce que la table est en insertion seule : lire une
décision doit reconstruire exactement la réponse d'origine, jamais la recalculer à partir de
données CORE-SIM qui peuvent avoir changé depuis.

## Rôles autorisés par endpoint

`POST /scoring` : `agent`, `superviseur` (pas `auditeur` — lecture seule par définition du rôle ;
pas `administrateur` — explicitement « sans scoring »). `GET /parametrage/grille` : `superviseur`,
`auditeur`, `administrateur`. `POST /parametrage/grille` : `superviseur` seul. Le reste
(`recherche`, `dossier`, `groupe`, `scoring/{id}`, `fiche`, `registre`) : tout rôle authentifié,
avec le cloisonnement par agence ci-dessus en plus pour `agent`.
