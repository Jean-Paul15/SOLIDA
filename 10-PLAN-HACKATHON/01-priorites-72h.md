# Plan des 72 heures

## Règle qui prime sur tout

> On ne commence rien de P1 tant que **tout** P0 n'est pas fonctionnel de bout en bout.

Le risque majeur d'un hackathon n'est pas de manquer d'ambition, c'est d'avoir six choses à 80 %
et rien à 100 % le troisième jour à 18 h.

## Jour 1 — Le socle

### Matin (08h00 – 13h00)

| Créneau | Action | Qui |
|---|---|---|
| 08h00 – 08h30 | Installation, réseau, `docker compose up`, vérification que tout démarre chez tous | Tous |
| 08h30 – 09h00 | Relecture du périmètre, répartition, rappel des contrats | Tous |
| 09h00 – 11h00 | Génération de CORE-SIM, contrôles de cohérence | Données |
| 09h00 – 11h00 | Squelette API, connexions, sonde de santé | Backend |
| 09h00 – 11h00 | Design system, primitives, écran de recherche | Front |
| 11h00 – 13h00 | Features individuelles, jeu d'entraînement | Données / ML |
| 11h00 – 13h00 | Endpoints recherche et dossier | Backend |
| 11h00 – 13h00 | Écran dossier 360° avec données factices | Front |

### Après-midi (14h00 – 20h00)

| Créneau | Action |
|---|---|
| 14h00 – 16h30 | Entraînement du socle EBM + régression de référence, premières métriques |
| 14h00 – 16h30 | Scorecard, grille, cascade — logique pure, testée |
| 14h00 – 16h30 | Écran de saisie de la demande |
| 16h30 – 19h00 | Câblage : entrée → features → modèle → score → réponse |
| 19h00 – 20h00 | **Premier score de bout en bout** + point d'équipe |

**Objectif de fin de jour 1 :** un score s'affiche dans le navigateur à partir d'un nom tapé.
Même moche, même approximatif. Si ce n'est pas le cas à 20 h, le jour 2 doit être consacré à
l'atteindre et P1 est abandonné.

## Jour 2 — La différenciation

### Matin

| Créneau | Action |
|---|---|
| 08h00 – 08h30 | Point : ce qui marche, ce qui bloque, réaffectation |
| 08h30 – 11h00 | Trajectoire d'épargne dynamique, agrégats solidaires (segment GIE) |
| 08h30 – 11h00 | Écran de résultat : score, tranche, contributions |
| 11h00 – 13h00 | Entraînement du modèle enrichi, comparatif à trois modèles |
| 11h00 – 13h00 | Persistance des décisions (obligatoire, pas optionnel) |

### Après-midi

| Créneau | Action |
|---|---|
| 14h00 – 16h00 | Cascade en conditions réelles, cas démarrage à froid |
| 14h00 – 16h00 | Écran du groupe de caution (segment GIE) |
| 16h00 – 18h00 | Fiche de justification et export PDF |
| 18h00 – 19h00 | Jeu de cas de démonstration figé et vérifié |
| 19h00 – 20h00 | **Première répétition du pitch**, à voix haute, chronométrée |

**Objectif de fin de jour 2 :** le parcours complet fonctionne avec les deux modes, sur des cas
choisis. La répétition du soir est non négociable — c'est elle qui révèle ce qui manque.

## Jour 3 — Consolidation et démonstration

### Matin

| Créneau | Action |
|---|---|
| 08h00 – 10h00 | Corrections issues de la répétition |
| 10h00 – 12h00 | Finitions visuelles, états vides, messages d'erreur |
| 12h00 – 13h00 | **Gel du code.** Plus aucune fonctionnalité |

**Le gel à 13 h est la décision la plus importante des trois jours.** Une fonctionnalité ajoutée
à 15 h casse une démonstration à 17 h. Après le gel : corrections de blocage uniquement, décidées
collectivement.

### Après-midi

| Créneau | Action |
|---|---|
| 14h00 – 15h30 | Répétitions du pitch, trois passages minimum |
| 15h30 – 16h30 | Plan de secours : captures d'écran, vidéo de la démonstration |
| 16h30 – 17h30 | Rejeu complet de `make demo` sur une machine propre |
| 17h30 – 20h00 | Pitch devant jury |

Le plan de secours n'est pas du pessimisme : le Wi-Fi partagé par cinq équipes tombe, un
rétroprojecteur ne reconnaît pas une résolution, un conteneur refuse de démarrer. Une vidéo de
90 secondes de la démonstration sauve la situation.

## Règles de fonctionnement pendant les 72 heures

| Règle | Motif |
|---|---|
| Point d'équipe de 15 minutes à 08h00, 13h00, 19h00 | Détecter un blocage avant qu'il ne coûte trois heures |
| Un blocage de plus de 45 minutes se dit à voix haute | Personne ne s'enferme |
| Personne ne travaille dans le module d'un autre | Conflits garantis sinon |
| Commit au moins toutes les deux heures | Perte maximale bornée |
| Sauvegarde de la base à chaque fin de journée, deux supports | Perdre les modèles du jour 2 serait fatal |
| Pause repas réellement prise | 12 heures par jour sans pause dégrade la qualité plus que le retard gagné |
| Interdiction d'ajouter une dépendance non prévue | Voir `AGENTS.md` |

## Décisions de renoncement préparées à l'avance

Il faut savoir **à l'avance** ce qu'on abandonne si on prend du retard. Décider sous pression est
la meilleure façon d'abandonner le mauvais élément.

| Retard constaté | On abandonne, dans cet ordre |
|---|---|
| Fin jour 1 sans score | Couche solidaire, écran de groupe, PDF. On livre un scoring individuel parfait |
| Fin jour 2 sans modèle enrichi | L'écran de groupe, on garde le comparatif à deux modèles |
| Jour 3 matin, PDF non prêt | On montre la fiche à l'écran, on explique l'export |
| Problème de démonstration | On passe à la vidéo de secours sans hésiter |

**Un scoring individuel impeccable avec une belle explication bat un système ambitieux qui plante.**
