# Construction du modèle — étapes du notebook

Ce fichier donne **les étapes** du notebook d'entraînement, pas le code. L'équipe ajoutera ses
propres principes et conventions. L'agent qui code le notebook (Claude Code ou Codex) suit ces
étapes dans l'ordre et s'arrête à toute décision non tranchée.

## Note à l'agent (protocole de collaboration)

- **C'est l'équipe qui impose le rythme.** L'agent avance étape par étape, s'arrête au bout de
  chacune, montre le résultat, attend le feu vert avant la suivante. Pas de notebook déroulé d'un
  bloc.
- L'agent suit **à la fois** les orientations de ce dossier (fondation) et les orientations
  techniques de l'équipe données en séance.
- **En cas de contradiction** entre les deux, l'agent ne tranche pas seul : il expose la
  contradiction, propose des options, et on décide ensemble.
- Toute décision absente de ce dossier remonte, elle ne s'improvise pas (voir `AGENTS.md`).

## Ce que l'équipe définit elle-même (pas l'agent, pas ce dossier)

Le **cœur du modèle** se décide pendant les trois jours, par l'équipe : les hyperparamètres de
l'EBM, la liste exacte des variables données au modèle, les arbitrages de tuning, le choix final du
seuil de défaut. Ce dossier donne les **principes et les garde-fous d'évaluation** à respecter, pas
ces décisions-là. L'agent applique les garde-fous ; l'équipe fixe les contraintes du modèle et les
lui impose, à respecter scrupuleusement.

## Étapes

### 1. Chargement et instantané
Charger la base CORE-SIM (lecture seule). Fixer une graine. Versionner l'instantané avec DVC. Aucune
transformation à ce stade.

### 2. Définition de la cible
Défaut = au moins une échéance à plus de 90 jours de retard (à confirmer avec le praticien).
Construire la variable cible au niveau crédit, avec la date à laquelle l'issue devient connue.

### 3. Découpage temporel
Découper par date de déblocage : entraînement (ancien), validation, test (récent, jamais consulté
avant l'évaluation finale). **Jamais de découpage aléatoire** (fuite).

### 4. Construction des features à `date_reference`
Calculer chaque feature à la date de la demande, jamais à aujourd'hui. Trois familles :
individuelles (dont trajectoire d'épargne), solidaires (agrégats du groupe hors sociétaire évalué,
sur le seul segment de groupe), sectorielles (adaptatives, écart à la base). Appliquer les trois
contrôles anti-fuite de `02-DONNEES/05`.

### 5. Contrôle des fuites
Vérifier explicitement : exclusion du sociétaire du taux de son groupe ; features à la bonne date ;
aucune variable dérivée du remboursement du crédit évalué. Tests automatiques.

### 6. Exclusion des variables sensibles
Retirer le sexe et tout substitut de la matrice. Test bloquant : l'entraînement échoue si une
variable sensible est présente.

### 6b. Sélection de variables et prétraitement
Appliquer les principes de `08-selection-variables-et-pretraitement.md` : sélection par l'importance
native d'EBM (pas d'IV/WoE ni de VIF), retrait de la redondance par corrélation, manquant traité
comme modalité, variables construites (trajectoire d'épargne, couche solidaire, secteur)
conservées. Sélection leak-free.

### 7. Entraînement des modèles
Trois modèles sur le même découpage : référence logistique (individuel), EBM socle (individuel),
EBM enrichi (individuel + couche solidaire + sectoriel). Tout journalisé dans MLflow.

### 8. Calibration
Diagnostiquer la calibration (courbe en déciles, Brier). Corriger si nécessaire (isotonique ou
Platt), sur le jeu de validation. Un modèle mal calibré n'est pas promu.

### 9. Évaluation
AUC, Gini, AUPRC, calibration, par segment (segment produit, zone, secteur, taille de groupe).
Comparatif des trois modèles. Apport de la couche solidaire et du sectoriel mesuré **sur la
population éligible**. Jamais d'accuracy comme métrique principale.

### 10. Scorecard et décomposition
Transformer PD en score entier (formule PDO), décomposer en points par variable. Vérifier
l'invariant : somme des points = score, sur 1000 dossiers. C'est la condition de la fiche de
justification.

### 11. Contrôle de non-discrimination
Vérifier a posteriori l'absence d'écart d'approbation par sexe et par zone à risque comparable.
Documenter tout arbitrage sur une variable substitut.

### 12. Promotion
Passer les contrôles de promotion de `07-MLOPS/01` (dont plafond d'AUC 0,88 pour détecter les
fuites). Enregistrer le modèle dans le registre MLflow, versionner l'artefact avec DVC.

## Repère de résultats attendus

D'après la validation du générateur (voir `solida-simulateur`), et sans qu'aucun de ces chiffres
n'ait été ciblé : l'AUC du socle émerge autour de **0,69-0,70**, dans le bas de la fourchette
sectorielle documentée (0,70-0,85), l'apport de la couche solidaire est **faible et bruité** sur le
seul segment de groupe (de l'ordre du centième d'AUC, probablement sous-estimé par le démarrage à
froid des groupes synthétiques). Ces valeurs se rapportent telles quelles au jury : elles sont la
conséquence de mécanismes calibrés sur la littérature, pas d'un objectif de performance. Un résultat
au-dessus de 0,88 doit faire suspecter une fuite avant de se réjouir.
