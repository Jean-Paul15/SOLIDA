# MLflow

## Configuration

| Élément | Choix |
|---|---|
| Base de suivi | PostgreSQL, base `solida` |
| Stockage d'artefacts | MinIO, compartiment `mlflow` |
| Interface | Port 5000, accès interne |

Deux backends distincts plutôt que le mode fichier : le mode fichier ne supporte pas plusieurs
utilisateurs simultanés, ce qui casse dès que deux personnes entraînent en parallèle — situation
garantie pendant un hackathon.

## Ce qui est journalisé à chaque exécution

### Paramètres
Type de modèle, hyperparamètres, graine, période d'entraînement, graine du générateur, liste des
variables, méthode de calibration.

### Métriques
AUC, Gini, AUPRC, Brier, ECE, AUC par segment, taux d'approbation à risque constant, gain de la couche solidaire.

### Artefacts
Modèle sérialisé, calibrateur, catalogue des variables, courbe ROC, courbe de calibration,
fonctions de forme des variables principales, rapport d'évaluation, instantané des données.

### Étiquettes
Auteur, branche, empreinte de commit, environnement, priorité de l'expérience.

## Organisation des expériences

| Expérience | Contenu |
|---|---|
| `solida-reference` | Régression logistique |
| `solida-socle` | EBM socle |
| `solida-enrichi` | EBM enrichi |
| `solida-ablation` | Études d'ablation de variables |

La séparation permet de comparer proprement. Tout mélanger dans une seule expérience rend
l'interface inutilisable au bout de quarante exécutions — ce qui arrive vite à trois personnes sur
deux jours.

## Registre de modèles

Trois modèles enregistrés : `solida-socle`, `solida-enrichi`, `solida-reference`.

Le passage à l'état `production` se fait par le registre, jamais en copiant un fichier à la main.
Le backend interroge le registre au démarrage pour charger la version active.

## Discipline

| Règle | Motif |
|---|---|
| Aucun entraînement hors MLflow | Un modèle non journalisé n'existe pas |
| Une exécution nommée | `socle-v3-sans-volatilite` et non `run-42` |
| Une note par exécution | Une phrase sur ce qui est testé et pourquoi |
| Les exécutions ratées sont conservées | Savoir ce qui ne marche pas a de la valeur |

La règle de nommage paraît anecdotique. À 22 h le jour 2, avec trente exécutions dans l'interface,
c'est la différence entre retrouver le bon modèle et le réentraîner.

## Périmètre hackathon

**P1, et fortement recommandé dès le jour 1.** Le coût d'installation est faible et le bénéfice
en démonstration est réel : montrer au jury l'historique des expériences et la comparaison
objective des trois modèles est autrement plus convaincant qu'un tableau de chiffres dans une
présentation.
