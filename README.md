# SOLIDA — Socle de principes et d'instructions

**Système de scoring d'octroi de microcrédit fondé sur la trajectoire d'épargne et le comportement de remboursement des sociétaires des Coopératives financières, avec enrichissement conditionnel sur le segment caution solidaire**

Hackathon National d'Innovation CIF / DigiCoop-WA+ — Thématique 02 — Lomé, 11-13 septembre 2026

---

## À quoi sert ce dossier

Ce dossier ne contient **aucun code applicatif**. Il contient les décisions, les principes et les
contrats qui gouvernent le code. Il a trois destinataires :

1. **Les membres de l'équipe humaine**, pour travailler en parallèle sans se bloquer.
2. **Claude Code**, qui doit disposer du contexte complet avant de produire quoi que ce soit.
3. **Codex**, qui exécute bien mais n'invente pas : tout ce qui n'est pas écrit ici, il ne le devinera pas.

> Règle fondatrice : **si une décision n'est pas écrite dans ce dossier, elle n'existe pas.**
> Un agent qui a besoin d'une décision absente doit la faire remonter, pas l'improviser.

---

## Ordre de lecture

| Si vous êtes… | Lisez dans cet ordre |
|---|---|
| Nouveau sur le projet | `00-CONTEXTE/` en entier, puis `01-ARCHITECTURE/01` et `04` |
| Agent IA (Claude / Codex) | `AGENTS.md`, puis `00-CONTEXTE/`, puis le dossier de votre périmètre |
| Sur le backend | `01-ARCHITECTURE/`, `04-BACKEND/`, `02-DONNEES/`, `08-SECURITE/` |
| Sur le modèle | `03-MODELE/`, `02-DONNEES/`, `07-MLOPS/` |
| Sur le front | `05-FRONTEND/` en entier, puis `01-ARCHITECTURE/05` (contrats) |
| Sur l'infra | `06-INFRA/`, `09-DEVOPS/`, `07-MLOPS/` |
| Le jour J | `10-PLAN-HACKATHON/` d'abord |

---

## Arborescence

```
SOLIDA-FOUNDATION/
├── README.md                    Ce fichier
├── AGENTS.md                    Protocole obligatoire pour Claude Code et Codex
├── .gitignore.template          À copier à la racine du dépôt de code
├── assets/                      Logo, note de présentation
├── 00-CONTEXTE/                 Projet, glossaire, périmètre, journal de décisions
├── 01-ARCHITECTURE/             Principes, Clean Architecture, SOLID, modules, contrats
├── 02-DONNEES/                  Schémas, générateur, contrat d'intégration, qualité, gouvernance
├── 03-MODELE/                   Modélisation, features, scorecard, cascade, évaluation
├── 04-BACKEND/                  API, conventions Python, auth, batch, observabilité
├── 05-FRONTEND/                 UX, design system, librairies, écrans, export PDF, motion
├── 06-INFRA/                    Stack, PostgreSQL, MinIO, configuration
├── 07-MLOPS/                    Cycle de vie modèle, MLflow, DVC, dérive, monitoring
├── 08-SECURITE/                 Principes, données perso, audit, secrets, inventaire, repos/transit/connexion
├── 09-DEVOPS/                   Git, hooks, CI, tests, definition of done
├── 10-PLAN-HACKATHON/           Priorités 72h, répartition, checklists, démo
└── 99-QUESTIONS-OUVERTES.md     Ce qui reste à trancher — à lire en premier
```

---

## Deux systèmes distincts, ne jamais les confondre

C'est la distinction structurante de tout le projet. Elle est détaillée dans
`01-ARCHITECTURE/06-frontiere-sim-vs-solida.md` et doit être comprise avant tout développement.

| | **CORE-SIM** | **SOLIDA** |
|---|---|---|
| Rôle | Simule le système de gestion d'une coopérative financière | Le produit que nous construisons |
| Propriétaire dans la vraie vie | L'IMF | Nous |
| Contenu | Sociétaires, comptes, crédits, remboursements, groupes | Features (dont trajectoire d'épargne), couche solidaire, modèles, scores, décisions, audit |
| Base de données | `coresim` (PostgreSQL) | `solida` (PostgreSQL) |
| Accès | **Lecture seule** depuis SOLIDA | Lecture / écriture |
| Après le hackathon | Remplacé par le vrai SI de l'IMF | Inchangé |

SOLIDA ne doit **jamais** écrire dans CORE-SIM. Toute écriture dans CORE-SIM est un bug d'architecture,
pas un détail d'implémentation.

---

## État du projet

| Élément | État |
|---|---|
| Note de présentation (dossier de candidature) | Rédigée — `assets/note-presentation-solida.pdf` |
| Schéma de données | Rédigé, **en attente de validation par un praticien IMF** |
| Principes et architecture | Ce dossier (auth FastAPI-Users, gouvernance, DVC, motion inclus) |
| Code | Non démarré |

**Date limite de dépôt du dossier de candidature : 23 août 2026, 23h59 GMT+0.**
