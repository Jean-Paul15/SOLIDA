# Sélection de variables et prétraitement — principes

Ce fichier fixe la stratégie de sélection de variables et de prétraitement, adaptée à EBM et au
scoring de crédit. Aucun code : uniquement les principes. L'équipe et les experts arrêtent le choix
final des variables le jour J.

## Méthode de sélection retenue : l'importance native d'EBM

EBM fournit une importance **exacte** par variable et par interaction, sans SHAP ni calcul post-hoc.
C'est le sélecteur de référence pour un modèle non-linéaire, et c'est ce qu'on utilise.

Protocole :
1. Entraîner un premier EBM sur toutes les variables candidates, **sur l'entraînement seulement**.
2. Lire son importance globale.
3. Retirer les variables à contribution quasi nulle (bruit) et les redondances.
4. Réentraîner sur le jeu réduit ; garder si la performance tient et si la fiche de justification
   est plus lisible.

## Ce qu'on n'utilise pas, et pourquoi (choix assumé, défendable devant le jury)

- **Pas d'Information Value / Weight of Evidence comme sélecteur.** L'IV/WoE est l'outil de l'ère
  scorecard logistique ; il mesure une force **univariée et linéaire** (en log-odds). Pour un modèle
  qui capte les non-linéarités et les interactions, l'importance native d'EBM est plus fidèle. Si le
  jury demande « pourquoi pas l'IV ? », c'est la réponse : ce n'est pas un oubli, c'est un choix.
- **Pas de VIF.** Le VIF est un diagnostic de colinéarité pour les modèles linéaires. Le boosting
  cyclique en round-robin d'EBM (une variable à la fois, faible taux d'apprentissage) atténue déjà
  la colinéarité par construction ; le VIF n'apporte rien de plus.

## La redondance survit, même sans VIF

Abandonner le VIF ne veut pas dire ignorer la redondance. Deux variables très corrélées poussent
EBM à modéliser des **interactions parasites** entre elles et laissent une seule variable **dominer**,
ce qui dégrade l'interprétabilité et la fiche. On garde donc un contrôle simple : une matrice de
corrélation, et pour chaque paire fortement corrélée on conserve la plus interprétable. C'est de la
redondance, pas du VIF.

## Les interactions : EBM les trouve, on ne les fabrique pas à la main

EBM détecte et sélectionne automatiquement les interactions par paires (procédure FAST / GA²M). On
ne crée donc **aucun** terme d'interaction à la main (revenu × durée, etc.) — EBM le fait mieux et
en garde la trace exacte.

## Mais les variables construites restent le cœur : EBM ne les invente pas

Contresens à éviter absolument : « EBM détecte les interactions » ne signifie pas « pas besoin de
feature engineering ». EBM combine les **colonnes existantes** ; il ne peut pas inventer une variable
absente des données brutes. Or nos différenciateurs — trajectoire d'épargne dynamique (tendance, effort,
ancienneté de la relation), taux de remboursement du groupe hors soi sur le segment solidaire,
tendance d'impayés du secteur, ratios d'endettement — sont des variables **construites** à partir
des tables brutes du portefeuille, sans jamais recourir à une structure de graphe (voir
`01-ARCHITECTURE/07`, ADR-016). Elles n'existent nulle part avant qu'on les calcule. **Elles sont la valeur du projet, on les garde.** La règle : interactions entre
colonnes = EBM ; variables construites = nous.

## Valeurs manquantes : informatives, pas imputées naïvement

En crédit, l'absence est souvent prédictive (un revenu non déclaré dit quelque chose). EBM traite le
manquant comme une **modalité à part entière**. On ne l'impute donc pas naïvement : on laisse
« manquant » être sa propre catégorie, et sa contribution devient lisible dans la shape function.
C'est cohérent avec l'injection volontaire de valeurs manquantes réalistes dans le générateur.

## Contraintes de monotonie (optionnel, P2)

Là où le sens métier est clair (endettement plus élevé → risque plus élevé), on peut imposer la
monotonie pour renforcer la confiance et éviter des oscillations bruitées. À appliquer **après**
l'entraînement, pas pendant : durant l'ajustement, le boosting peut compenser une contrainte via une
variable corrélée et masquer les violations.

## Sélection sans fuite, toujours

La sélection se décide sur l'entraînement et la validation **seulement**, jamais sur le test — sinon
l'information du test fuit dans le choix des variables (biais de sélection). Pour la robustesse :
sélection par **stabilité** sur une validation croisée **temporelle** (on garde les variables
retenues dans la majorité des plis). Une variable stable dans le temps est un vrai signal ; une
variable qui n'apparaît que dans un pli est probablement du bruit.

## Protection métier et réglementaire

Deux retraits qui ne sont pas statistiques : on **garde** les variables que le métier attend
(endettement, régularité d'épargne) même si un run les classe un cran bas — leur absence de la fiche
serait suspecte pour un banquier. Et on **exclut** le sexe et tout substitut, conformément à la
non-discrimination (`06-ethique-et-non-discrimination.md`).

## Rappel de réalisme

La performance n'est jamais ciblée ; elle émerge des mécanismes calibrés sur la littérature du
défaut en microfinance (voir `02-DONNEES/03-generateur-principes.md`), puis **validée** contre la
fourchette documentée du secteur, de l'ordre de **0,70 à 0,85 d'AUC**. Une AUC proche de 0,90 sur
nos données synthétiques serait un drapeau rouge de fuite qu'un jury sectoriel repérerait
immédiatement — ce n'est pas un objectif à atteindre, c'est une alerte à surveiller.

## Périmètre hackathon

**P1 :** importance native EBM, retrait bruit et redondance, protection métier, manquant-comme-
modalité.
**P2 :** contraintes de monotonie, sélection par stabilité sur CV temporelle.
Décision finale des variables : équipe + experts métier le jour J.
