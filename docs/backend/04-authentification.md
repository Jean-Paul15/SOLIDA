# Authentification

## FastAPI-Users, session révocable unique

Un seul mécanisme d'authentification : cookie `solida_session` (httpOnly, `SameSite=Lax`,
`Secure` activé uniquement en production), jeton opaque stocké dans `access_token` et vérifié
à chaque requête par `DatabaseStrategy` — révocable immédiatement (déconnexion, ou blocage d'un
compte), durée de vie absolue huit heures **et** expiration par inactivité de 15 minutes vérifiée
côté serveur à chaque requête (`derniere_activite_le` sur `access_token`, mise à jour par
`current_active_user` dans `infrastructure/auth/current_user.py`) — un minuteur uniquement côté client se
contourne, cf. OWASP Session Management Cheat Sheet. Pas de JWT à part : la simplicité et la
révocabilité totale priment sur la réduction de charge sur `access_token`, négligeable à l'échelle
d'une coopérative.

**Une seule session active par compte** : toute nouvelle connexion révoque les jetons précédents du
même utilisateur (`revoke_user_tokens`) — motivé par le risque explicite d'un poste
partagé en agence, pas seulement un choix de simplicité.

Connexion par `identifiant` (pas par e-mail) : `UserManager.authenticate_by_identifier`
reproduit la mitigation de `BaseUserManager.authenticate()` contre les attaques par mesure de temps
(un mot de passe est haché même quand l'identifiant n'existe pas). Verrouillage après 5 échecs de
connexion sur 15 minutes pour un même `identifiant` (comptés dans `journal_audit`, réponse 429
générique — ne révèle pas si le compte existe).

## Politique de mot de passe

`domain/rules/mot_de_passe.py` : 8 à 64 caractères (NIST SP 800-63B rev.4 — 8 est le plancher SHALL
quel que soit le nombre de facteurs, pas de MFA dans ce système), aucune règle de composition
(interdite explicitement par la même norme), comparaison à une liste locale de mots de passe
courants (`infrastructure/mots_de_passe_courants.txt`, aucun appel réseau — cohérent avec la
souveraineté des données). Appliquée uniquement à la création volontaire d'un mot de passe
(`POST /api/v1/auth/changer-mot-de-passe`), jamais au mot de passe partagé des comptes de démo
(qui doit de toute façon être changé dès la première connexion, voir plus bas).

## Endpoints

`POST /api/v1/auth/connexion` (`{identifiant, mot_de_passe}` → `{nom, agence, doit_changer_mot_de_passe}`
+ cookie), `POST /api/v1/auth/deconnexion` (révoque le jeton en base puis efface le cookie),
`GET /api/v1/auth/moi` (relit l'utilisateur courant depuis le cookie), `POST
/api/v1/auth/changer-mot-de-passe` (`{mot_de_passe_actuel, nouveau_mot_de_passe}` — exige le mot de
passe actuel même en session authentifiée, défense en profondeur contre une session laissée
ouverte ; révoque toutes les sessions du compte après changement, y compris la courante).

## Rôles et cloisonnement

Quatre rôles en base (`utilisateur.role`) : `agent` (limité à son `agence_id`), `superviseur`,
`auditeur`, `administrateur`. `require_role(*roles)` (dépendance FastAPI) refuse l'accès à
l'endpoint si le rôle courant n'y figure pas — **un contrôle nécessaire mais pas suffisant** : le
cloisonnement par agence pour le rôle `agent` doit être revérifié dans chaque cas d'usage qui lit
ou écrit une donnée liée à une agence, jamais seulement à l'entrée du routeur. Le frontend peut
cacher un bouton ; seule cette double vérification côté serveur fait foi.

## Provisioning et cycle de vie des comptes

Aucun endpoint HTTP ne crée, débloque ou modifie un compte — choix délibéré, surface d'attaque
nulle sur la gestion des comptes. Le seul mécanisme, pour la démonstration comme pour un usage
réel, est `infrastructure/cli_provisionner_comptes.py`, exécuté manuellement dans le conteneur
(`docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes ...`) :
`creer` (nouveau compte ou mise à jour nom/rôle/agence, mot de passe initial généré aléatoirement
si non fourni), `demo` (les cinq comptes de démonstration historiques, mot de passe partagé
`solida-demo`), `bloquer`/`debloquer` (bascule `is_active`, révoque les sessions ouvertes à
la désactivation, horodate `desactive_le`).

Tout compte créé via `creer` porte `doit_changer_mot_de_passe=true` : le frontend redirige
systématiquement vers `/changer-mot-de-passe` jusqu'au premier changement volontaire, quel que
soit l'écran demandé. Exception délibérée pour `demo` : ce sont des comptes de test au mot de
passe déjà connu de tous, forcer leur changement n'apporterait rien et ralentirait la démo.

## Simplification à noter

`utilisateur.agence_id` porte un vrai code `caisse_id` de CORE-SIM (`CAI-00`, `CAI-01`, ...), pas
un libellé affichable ni une table `agence` séparée — c'est cette valeur qui est comparée à
`societaires.caisse_id` pour le cloisonnement du rôle `agent`, elle doit donc rester un identifiant
réel, pas un nom de convenance. Conséquence : la réponse de connexion (`{nom, agence}`) affiche
le code brut ("CAI-00"), pas un nom de quartier — aucune table de correspondance code → libellé
n'existe dans CORE-SIM ni dans le schéma `solida`. Voir `03-decisions-provisoires-a-revoir.md`.
