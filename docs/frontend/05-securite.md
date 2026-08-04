# Sécurité — mesures appliquées

## Session

- Cookie `solida_session` : `httpOnly`, `sameSite=lax`, `secure` activé uniquement en production
  (pas de TLS en développement local — écart assumé, documenté ici plutôt que caché).
- Jamais de jeton en `localStorage`/`sessionStorage`.
- `frontend/proxy.ts` protège `/`, `/societaires/*`, `/scoring/*` : redirection vers `/connexion` en
  l'absence de session.

## En-têtes HTTP

`next.config.ts` pose `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` et
`Referrer-Policy: strict-origin-when-cross-origin` sur toutes les routes.

## Secrets

Aucun secret dans ce dépôt : la session de démonstration n'est pas un jeton signé, les identifiants
de démonstration (`lib/mocks/agents.ts`) sont volontairement publics et ne protègent aucune donnée
réelle. `.env.example` documente les variables attendues sans valeur exploitable.

## Conteneurs

Voir `05-docker-et-dev.md` pour le détail (utilisateur non-root, image minimale, aucun secret dans
l'image, réseau isolé).

## Hors périmètre de cette passe

Authentification réelle (FastAPI-Users, Argon2id), contrôle d'accès par rôle et par agence, CORS
(pas de backend séparé à ce stade), limitation de débit, TLS de bout en bout.
