# Câblage frontend → backend réel

## Réécriture, pas de proxy applicatif

`frontend/next.config.ts` réécrit `/api/v1/:path*` vers `${BACKEND_INTERNAL_URL}/api/v1/:path*`
(variable d'environnement, `http://api:8000` dans `docker-compose.yml`). Une route Next.js
locale existante (ex. `app/api/v1/sante/route.ts`, conservée comme sonde de vie du conteneur
`front` indépendante du backend) est toujours servie en priorité — Next.js vérifie le système de
fichiers avant d'appliquer une réécriture "afterFiles" (comportement documenté, vérifié avant
d'écrire la config). Toutes les autres routes `app/api/v1/**` (mocks) ont été supprimées : plus
rien ne les intercepte localement, donc la réécriture s'applique.

Les composants client (`lib/services/*`, formulaires) appelaient déjà `fetch("/api/v1/...")` en
chemin relatif : ils n'ont pas eu besoin d'être modifiés, la réécriture suffit côté navigateur.

## Server Components : le cookie ne traverse pas tout seul

Un fetch lancé depuis un Server Component (SSR) part du processus Next.js, pas du navigateur : il
ne porte aucun cookie automatiquement, et la réécriture ne s'applique qu'aux requêtes qui
traversent le serveur HTTP Next.js depuis l'extérieur. `lib/backend.ts` (`fetchBackend`) résout
les deux : il appelle le backend directement (`BACKEND_INTERNAL_URL`) et transmet explicitement
le cookie de la requête entrante (`next/headers` `cookies()`), avec `cache: "no-store"` — cette
donnée dépend de la session, la mise en cache de `fetch` la partagerait entre utilisateurs sinon.

`lib/session.ts` (`lireSession`) relit la session via `GET /api/v1/auth/moi` plutôt que de décoder
le cookie : celui-ci est un jeton opaque géré par FastAPI-Users, le frontend n'a aucun moyen de le
lire ni de lui faire confiance directement (cohérent avec la consigne de sécurité déjà appliquée
côté backend : ne jamais faire confiance au frontend).

## Écrans corrigés au passage

- **E7 (registre) et E8 (grille)** n'avaient jamais été câblés à un backend, même mock : E7 lisait
  `lib/mocks/decisions.ts` directement en Server Component, et le bouton "Enregistrer la grille"
  d'E8 ne faisait qu'un `setTimeout` sans aucun appel réseau. Les deux appellent maintenant les
  vrais endpoints (`GET /api/v1/registre`, `GET`/`POST /api/v1/parametrage/grille`), vérifié par
  une écriture réelle en base via l'interface (`grille_decision` contient la nouvelle version,
  avec le nom du superviseur connecté comme auteur, pas une valeur inventée).
- **"Dossiers récents"** sur l'écran de recherche (E1) : liste d'identifiants fictifs
  (`soc-adjo`, ...) codée en dur, incompatible avec les vrais identifiants CORE-SIM
  (`SOC-000000`). Supprimée — aucune fonctionnalité de « dossiers récents » n'est spécifiée nulle
  part, ce n'était qu'un reliquat de démonstration.
- **`GrilleParametrage`** initialisait ses curseurs sur des valeurs codées en dur qui
  correspondaient par coïncidence à la grille `v0.1` : ils partent maintenant de la configuration
  active réellement lue en base, `odds_reference` inclus (n'était pas exposé par l'écran avant,
  simplement recopié depuis la configuration active lors de l'enregistrement).

## Retiré

`frontend/lib/mocks/` (agents, décisions, sociétaires, scoring) et `frontend/app/api/v1/{auth,
scoring, societaires}/**`. Aucune donnée de démonstration ne reste dans le code applicatif.

## Vérifié

Parcours complet en navigateur réel (pas seulement `curl`) : connexion, recherche cloisonnée par
agence, dossier avec groupe de caution, calcul de score, fiche de justification, registre, et
écriture d'une nouvelle version de grille par un superviseur — persistée en base, vérifiée
directement en SQL après coup.
