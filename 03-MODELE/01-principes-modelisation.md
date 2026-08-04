# Principes de modélisation

## Les quatre modèles

| Nom | Rôle | Variables | Statut |
|---|---|---|---|
| **Référence logistique** | Étalon bancaire classique | Socle individuel | Obligatoire, sert la démonstration |
| **Socle EBM** | Modèle de production, toujours actif | Socle individuel | Obligatoire |
| **Enrichi EBM** | Modèle de production, sur le segment de groupe | Socle + couche solidaire | Obligatoire |
| Arbre de décision simple | Repli d'urgence | 5 variables | Optionnel |

Le comparatif des trois premiers **est un livrable**, pas un exercice académique. C'est ce qui
objective l'apport de la méthode plutôt que de le postuler, et cela sert directement le critère
« faisabilité technique et réalisme » (20 %).

## Pourquoi l'EBM

| Exigence | Réponse EBM |
|---|---|
| Interprétabilité | Modèle additif généralisé : contribution de chaque variable lisible directement |
| Décomposition exacte en points | La structure additive dans l'espace des log-odds rend la scorecard exacte |
| Légèreté | Aucune dépendance GPU, inférence en millisecondes, artefact de quelques Mo |
| Non-linéarités | Fonctions de forme par variable, contrairement à la régression logistique |
| Valeurs manquantes | Traitées nativement comme une modalité |

**Ce que l'EBM coûte :** entraînement plus lent qu'un XGBoost, performance légèrement inférieure
dans l'absolu sur des jeux très riches. Ce coût est accepté : l'explicabilité exacte n'est pas
négociable dans ce produit.

## Ce qui est interdit

| Interdit | Motif |
|---|---|
| Modèle d'ensemble par arbres en production (XGBoost, LightGBM, forêt) | Décomposition en points seulement approchée via SHAP |
| Réseau de neurones | Contredit légèreté et explicabilité |
| GNN et méthodes de graph ML | Supposent une structure de graphe dense qui n'existe pas dans un portefeuille de crédit individuel dominant (ADR-016) ; opaques et lourds de surcroît |
| Ajouter une variable sans la documenter | Rompt la reproductibilité |
| Variable sensible ou son substitut | Engagement de non-discrimination |

**Sur le graph ML (GNN, centralité) :** c'est la tentation naturelle dès qu'on évoque des cautions
solidaires. Elle est écartée après vérification, pas par principe. La CIF est un réseau de
coopératives d'**épargne-crédit** où le crédit est majoritairement individuel et adossé à l'épargne
nantie ; le crédit de groupe est un segment minoritaire. La densité d'interconnexions qu'exigent ces
méthodes n'existe donc pas : les appliquer reviendrait à extraire un signal d'une structure absente,
et produirait du bruit. Sur le segment de groupe, trois agrégats SQL simples (remboursement du
groupe hors soi, taille, « déjà secouru ») captent l'essentiel de ce que la structure réelle porte.
C'est une décision d'ingénierie qui tient devant un mentor connaissant la structure réelle d'un
portefeuille mutualiste — et c'est un argument d'innovation plus solide que d'empiler une méthode
séduisante sur une donnée qui n'existe pas.

## Variable cible

Défaut = au moins une échéance présentant plus de **90 jours** de retard sur la vie du crédit.
Seuil aligné sur la notion de créance en souffrance des SFD de l'UEMOA, **à confirmer par le
praticien**, notamment pour le crédit agricole.

Variantes évaluées : PAR30, PAR60, PAR90. Celle retenue est celle qui correspond à la pratique
effective de l'institution.

**Crédits restructurés :** décision à valider. Par défaut, comptés en défaut, car une
restructuration révèle une difficulté avérée.

## Déséquilibre de classes

Taux de défaut autour de 9 %. Ce déséquilibre est modéré et ne justifie **pas** un
rééchantillonnage agressif.

| Technique | Décision |
|---|---|
| SMOTE et variantes | **Non.** Crée des sociétaires synthétiques qui n'existent pas, dégrade la calibration |
| Sous-échantillonnage | Non, perte d'information |
| Pondération de classe | Oui, si nécessaire, avec recalibration ensuite |
| Rien | À tester en premier |

**La calibration prime sur l'équilibrage.** Un modèle bien calibré sur données déséquilibrées est
supérieur à un modèle équilibré artificiellement dont les probabilités ne veulent plus rien dire,
puisque toute la scorecard repose sur la validité des probabilités.

## Reproductibilité

Graine fixée, versions épinglées, données versionnées par la graine du générateur, expériences
suivies dans MLflow. Un entraînement doit être rejouable à l'identique.
