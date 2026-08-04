# Authentification

## FastAPI-Users, session révocable unique

Un seul mécanisme d'authentification : cookie `solida_session` (httpOnly, `SameSite=Lax`,
`Secure` activé uniquement en production), jeton opaque stocké dans `access_token` et vérifié
à chaque requête par `DatabaseStrategy` — révocable immédiatement (déconnexion, ou blocage d'un
compte), durée de vie huit heures. Pas de JWT à part : la simplicité et la révocabilité totale
priment sur la réduction de charge sur `access_token`, négligeable à l'échelle d'une coopérative.

Connexion par `identifiant` (pas par e-mail) : `GestionnaireUtilisateurs.authentifier_par_identifiant`
reproduit la mitigation de `BaseUserManager.authenticate()` contre les attaques par mesure de temps
(un mot de passe est haché même quand l'identifiant n'existe pas).

## Endpoints

`POST /api/v1/auth/connexion` (`{identifiant, mot_de_passe}` → `{nom, agence}` + cookie),
`POST /api/v1/auth/deconnexion` (révoque le jeton en base puis efface le cookie),
`GET /api/v1/auth/moi` (relit l'utilisateur courant depuis le cookie — sert de base à la
vérification de session côté frontend une fois les mocks retirés).

## Rôles et cloisonnement

Quatre rôles en base (`utilisateur.role`) : `agent` (limité à son `agence_id`), `superviseur`,
`auditeur`, `administrateur`. `exige_role(*roles)` (dépendance FastAPI) refuse l'accès à
l'endpoint si le rôle courant n'y figure pas — **un contrôle nécessaire mais pas suffisant** : le
cloisonnement par agence pour le rôle `agent` doit être revérifié dans chaque cas d'usage qui lit
ou écrit une donnée liée à une agence, jamais seulement à l'entrée du routeur. Le frontend peut
cacher un bouton ; seule cette double vérification côté serveur fait foi.

## Comptes de démonstration

Cinq comptes semés par migration (`316b99efb09e_seed_utilisateurs_demo.py`), un par rôle plus un
second agent, mot de passe `solida-demo` pour tous : `agent.be`, `agent.agoe` (identifiant et nom
repris du mock frontend pour ne pas casser la démo), `superviseur.reseau`, `auditeur.interne`,
`administrateur.systeme`. À supprimer ou remplacer avant tout déploiement réel.

## Simplification à noter

`utilisateur.agence_id` porte un vrai code `caisse_id` de CORE-SIM (`CAI-00`, `CAI-01`, ...), pas
un libellé affichable ni une table `agence` séparée — c'est cette valeur qui est comparée à
`societaires.caisse_id` pour le cloisonnement du rôle `agent`, elle doit donc rester un identifiant
réel, pas un nom de convenance. Conséquence : la réponse de connexion (`{nom, agence}`) affiche
le code brut ("CAI-00"), pas un nom de quartier — aucune table de correspondance code → libellé
n'existe dans CORE-SIM ni dans le schéma `solida`. Voir `03-decisions-provisoires-a-revoir.md`.
