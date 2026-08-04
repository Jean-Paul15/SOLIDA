# Répartition des responsabilités

## Principe

Un module a **un propriétaire unique**. Deux personnes ne modifient jamais le même module en même
temps. Le propriétaire décide, les autres proposent.

## Rôles à couvrir

L'équipe compte 3 à 5 personnes. Voici les rôles à pourvoir, sachant qu'une personne peut en
cumuler deux et qu'il n'y a pas forcément une personne par rôle.

### R1 — Données et simulateur
**Modules :** A1 à A7, C1, C6
**Livrables :** CORE-SIM peuplé et cohérent, adaptateur de lecture, contrôles de qualité
**Compétences :** Python, SQL, statistiques descriptives
**Chemin critique :** oui — tout le monde attend ses données au jour 1

### R2 — Modèle et features
**Modules :** C2, C3, C4, D1 à D7
**Livrables :** features (dont trajectoire d'épargne), couche solidaire, trois modèles, calibration, comparatif
**Compétences :** Python, scikit-learn, InterpretML, SQL (agrégats)
**Chemin critique :** oui à partir du jour 1 après-midi

### R3 — Backend et domaine
**Modules :** B1 à B7, E1 à E9, F1 à F3
**Livrables :** règles métier, cas d'usage, API, authentification, audit
**Compétences :** Python, FastAPI, PostgreSQL, architecture
**Chemin critique :** oui — c'est le point de rencontre de tout

### R4 — Front
**Modules :** G1 à G11
**Livrables :** design system, six écrans P0/P1, export PDF côté affichage
**Compétences :** Next.js, TypeScript, Tailwind, sens du détail visuel
**Chemin critique :** oui à partir du jour 1 après-midi

### R5 — Métier, produit et pitch
**Livrables :** cohérence métier, jeu de cas de démonstration, argumentaire, slides, pitch
**Compétences :** compréhension de la microfinance, communication, esprit de synthèse
**Chemin critique :** non, mais **détermine la note** — les critères non techniques pèsent 45 %

## Répartitions selon l'effectif

### À trois
| Personne | Rôles |
|---|---|
| 1 | R1 + R2 (données et modèle) |
| 2 | R3 (backend et domaine) |
| 3 | R4 + R5 (front et pitch) |

Tendu mais faisable. Le périmètre P1 doit être revu à la baisse dès le départ.

### À quatre
| Personne | Rôles |
|---|---|
| 1 | R1 puis renfort R2 |
| 2 | R2 |
| 3 | R3 |
| 4 | R4 + R5 |

### À cinq — configuration idéale
| Personne | Rôles |
|---|---|
| 1 | R1 |
| 2 | R2 |
| 3 | R3 |
| 4 | R4 |
| 5 | R5 + renfort là où ça bloque |

La cinquième personne ne doit **pas** avoir de module critique : elle est la variable
d'ajustement, elle prépare le pitch, elle teste, elle détecte les incohérences métier, et elle
absorbe l'imprévu. C'est le rôle le plus sous-estimé et souvent celui qui fait gagner.

## Points de couplage à surveiller

| Couplage | Risque | Prévention |
|---|---|---|
| R1 → R2 | R2 attend les données | R1 livre un échantillon dès 10h le jour 1 |
| R2 → R3 | R3 attend le modèle | R3 développe contre `ModeleConstant` |
| R3 → R4 | R4 attend l'API | R4 développe contre les contrats et des données factices |
| R2 ↔ R3 | Désaccord sur le format des contributions | Contrat gelé avant le hackathon |

**Les trois premières lignes sont la raison d'être des contrats d'interface.** Correctement
appliqués, personne n'attend personne.

## Qui décide quoi

| Décision | Qui tranche |
|---|---|
| Contrat d'interface | Équipe entière, avant le hackathon |
| Choix technique dans un module | Le propriétaire |
| Renoncement de périmètre | Équipe, selon le tableau préparé |
| Contenu du pitch | R5, avec validation de l'équipe |
| Arrêt du développement | Chef d'équipe, à 13h le jour 3 |

## À remplir avant le départ

| Rôle | Nom | Téléphone | Environnement prêt |
|---|---|---|---|
| R1 | | | ☐ |
| R2 | | | ☐ |
| R3 | | | ☐ |
| R4 | | | ☐ |
| R5 | | | ☐ |
