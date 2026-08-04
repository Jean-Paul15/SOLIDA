# Stack technique et justifications

Chaque choix est justifié par les trois contraintes permanentes : légèreté, explicabilité,
souveraineté. Une justification par « c'est ce qui se fait » n'est pas recevable.

## Vue d'ensemble

| Couche | Choix | Version | Justification |
|---|---|---|---|
| Base de données | PostgreSQL | 16 | Deux bases distinctes, `pg_trgm` pour la recherche floue, universellement connu |
| Backend | FastAPI + Python | 3.12 | **Un seul** backend (ADR-010), même langage que le ML, typage |
| Auth | FastAPI-Users | à épingler | MIT, embarquée, pas de service d'IAM (ADR-009) |
| ML | InterpretML (EBM) | à épingler | Seul modèle offrant une décomposition exacte en points |
| Couche solidaire | SQL classique (agrégats `GROUP BY`) | — | Voir ADR-016 : aucune base graphe, la densité de réseau nécessaire n'existe pas |
| Front | Next.js | 16.3.0 | App Router, Server Components, écosystème |
| Style | Tailwind CSS | 4 | Jetons via `@theme`, cohérent avec shadcn |
| Composants | shadcn/ui | — | Accessible, modifiable, non versionné en dépendance |
| Stockage objet | MinIO | — | Compatible S3, auto-hébergé, souverain |
| Suivi ML | MLflow | — | Registre de modèles + suivi d'expériences |
| Versionnage données/modèles | DVC | à épingler | Apache 2.0, remote MinIO, complément de MLflow (ADR-011) |
| Qualité de données | Pandera | à épingler | Validation de schéma légère, native pandas |
| Métriques | Prometheus + Grafana | — | Standard, auto-hébergeable |
| Conteneurs | Docker + Compose | — | Suffisant. Pas de Kubernetes |
| PDF | WeasyPrint | — | HTML+CSS vers PDF, typographie française correcte |

**Toutes les versions sont épinglées.** L'agent doit vérifier la version courante et sa compatibilité
avant de l'inscrire, conformément au protocole de recherche d'`AGENTS.md`.

## Next.js 16 plutôt que 15

Vérifié sur le registre npm et la documentation officielle (nextjs.org/docs, août 2026) : Next.js 15
est en maintenance LTS (dernier correctif 15.5.22), Next.js 16.3.0 est la version courante. Choix de
l'équipe : prendre la dernière version plutôt que rester sur 15.

**Conséquences techniques à connaître pour tout le code front :**
- Node.js **≥ 20.9.0** requis (image Docker : `node:22-slim`).
- Turbopack est stable et actif par défaut pour `next dev` et `next build` — plus besoin du flag
  `--turbopack`.
- Les API asynchrones (`cookies()`, `headers()`, `params`, `searchParams`, etc.) n'ont plus de mode
  de compatibilité synchrone : toujours `await`.
- Le fichier `middleware.ts` est renommé `proxy.ts` (export `proxy`, plus `middleware`).
- La commande `next lint` est supprimée : lint via `eslint` directement (`eslint-config-next` 16.x,
  flat config).
- TypeScript minimum requis par Next 16 : 5.1.0. Le projet épingle **TypeScript 5.9.3**, pas la
  dernière version publiée (7.0.2) : TypeScript 7 est un portage natif en Go sans API de compilateur
  JS stable, et la documentation Next.js elle-même signale que sa détection TypeScript peut échouer
  avec ce paquet. 5.9.3 est la dernière version de la lignée stable, compatible avec tout
  l'outillage (ESLint, shadcn/ui, Next).

## Vitest pour les tests unitaires front

Aucun test runner JS/TS n'était listé dans ce document. `09-DEVOPS/04-tests-et-definition-of-done.md`
exige pourtant de tester la logique déterministe (formatage des montants, calcul d'échéance et de
taux d'endettement de l'écran E3). Choix de l'équipe : **Vitest** (dernière version stable
`4.1.10`), zéro conflit avec Next.js/Turbopack, dépendance de développement uniquement.

## PostgreSQL plutôt que Supabase

Voir ADR-005. Résumé du raisonnement :

Supabase auto-hébergé empile Kong, GoTrue, PostgREST, Realtime, Storage et Studio. Nous
n'utiliserions que l'authentification et le stockage, soit une fraction. Six services à exploiter
dans une coopérative dotée d'un informaticien à temps partiel, c'est exactement ce que nous
reprochons aux solutions inadaptées au terrain.

Supabase géré résout l'exploitation mais place les données des sociétaires hors du périmètre de la
coopérative, ce qui contredit frontalement notre argument de souveraineté et serait relevé par le
jury.

PostgreSQL nu : un service, un fichier de configuration, une sauvegarde, connu de tous les
prestataires informatiques de Lomé. C'est la décision cohérente avec le discours produit.

**Contrepartie assumée :** il faut écrire l'authentification. C'est environ une journée de travail,
et cela donne un contrôle total sur le journal d'audit.

## Docker Compose plutôt que Kubernetes

Une coopérative n'a pas d'équipe plateforme. Docker Compose se lit, se démarre et se répare. C'est
aussi ce qui permet de montrer au jury un système entier qui démarre en une commande.

## Services du compose

| Service | Port | Rôle |
|---|---|---|
| `postgres-coresim` | 5433 | Base du SI simulé |
| `postgres-solida` | 5432 | Base SOLIDA |
| `api` | 8000 | FastAPI |
| `front` | 3000 | Next.js |
| `minio` | 9000 / 9001 | Stockage objet |
| `mlflow` | 5000 | Suivi et registre |
| `prometheus` | 9090 | Métriques (P2) |
| `grafana` | 3001 | Tableaux (P2) |

Deux instances PostgreSQL distinctes plutôt que deux bases dans une même instance : cela rend la
frontière physique et empêche toute jointure accidentelle. C'est un garde-fou mécanique, conforme
au principe 9 de `01-ARCHITECTURE/01`.

## Ressources cibles

L'ensemble doit tourner sur une machine à 8 Go de RAM et 4 cœurs. Chaque poste de développement de
l'équipe doit pouvoir lancer la pile complète, sinon le travail en parallèle devient impossible.

## Dépendances interdites

| Interdit | Motif |
|---|---|
| Tout service cloud propriétaire avec données métier | Souveraineté |
| Base de données graphe dédiée | Voir ADR-016 |
| Kafka, Spark, Airflow | Disproportionnés, contredisent la légèreté |
| Kubernetes | Idem |
| Librairie de composants non listée dans `05-FRONTEND/03` | Dérive de stack |
| API LLM | Aucun besoin, et enverrait des données hors périmètre |

Le dernier point mérite d'être explicite : SOLIDA ne contient **aucun appel à un modèle de langage**.
Le produit est un système de scoring statistique interprétable. Introduire un LLM contredirait
l'explicabilité, la légèreté et la souveraineté d'un seul coup.
