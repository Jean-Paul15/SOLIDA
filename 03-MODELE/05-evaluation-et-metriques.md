# Évaluation

## Métriques retenues

L'exactitude brute est **proscrite** comme métrique principale : sur un jeu à ~9 % de défaut, un
modèle prédisant systématiquement « pas de défaut » dépasse 90 % et ne sert à rien. Un jury
sectoriel relèvera immédiatement une présentation fondée sur l'accuracy.

### Discrimination

| Métrique | Fourchette de validation | Commentaire |
|---|---|---|
| **AUC-ROC** | 0,70 – 0,85 | Métrique principale. **Fourchette de validation, pas cible** : la performance émerge des mécanismes, on vérifie ensuite qu'elle y tombe (voir `02-DONNEES/03-generateur-principes.md`). Le socle du prototype sort autour de 0,69-0,70 |
| **Gini** | `2 × AUC − 1` | Langage du secteur bancaire |
| **AUPRC** | rapportée | Plus informative en classes déséquilibrées, préférée au KS ici |

Au-delà de 0,85-0,88 d'AUC sur données synthétiques, **suspecter une fuite** avant de se réjouir.

### Calibration

| Métrique | Cible |
|---|---|
| Brier score | Le plus bas possible, comparé entre modèles |
| Erreur de calibration attendue (ECE) | < 0,03 |
| Courbe de calibration en déciles | Écart maximal < 5 points |

### Métriques opérationnelles

Ce sont celles qui parlent au jury et à une direction d'IMF.

| Indicateur | Définition |
|---|---|
| **Taux d'approbation à risque constant** | Part de dossiers accordés pour un taux de défaut cible donné |
| **Taux de défaut évité** | Défauts qui auraient été refusés par la grille |
| **Taux de bons refusés** | Contrepartie, à ne jamais masquer |
| **Gain de la couche solidaire** | Écart d'AUC entre modèle enrichi et socle sur la population éligible (segment de groupe) |

Le **taux de bons refusés** doit figurer dans toute présentation. Ne montrer que les défauts évités
est une présentation partiale, et un jury financier le verra.

## Protocole comparatif

Les trois modèles sont évalués sur le **même jeu de test**, avec le **même découpage temporel**.

| Modèle | Population d'évaluation |
|---|---|
| Référence logistique | Toute la population |
| Socle EBM | Toute la population |
| Enrichi EBM | **Uniquement la population éligible au mode enrichi** |

**Point méthodologique important :** comparer l'enrichi sur toute la population serait
malhonnête, puisqu'il ne s'applique pas à tous. La comparaison juste est socle vs enrichi
**sur la sous-population éligible aux deux**. Ce détail est exactement le genre de chose qu'un
mentor technique vérifiera.

## Analyse par segment

L'agrégat masque les problèmes. Performance rapportée par : cycle, zone, secteur, taille de groupe,
agence, tranche de montant.

Un modèle correct globalement mais mauvais sur les primo-emprunteurs ruraux est un modèle
inutilisable en pratique, puisque c'est une part importante de la clientèle visée.

## Contrôle de non-discrimination

Bien que le sexe soit exclu du modèle, on vérifie **a posteriori** que le taux d'approbation ne
présente pas d'écart substantiel entre hommes et femmes à profil de risque comparable. Un écart
significatif signalerait qu'une variable retenue en constitue un substitut.

Le même contrôle est appliqué par zone (urbain / rural).

## Stabilité

Modèle réentraîné sur 5 découpages temporels glissants. Écart-type de l'AUC inférieur à 0,03.
Un modèle instable d'une période à l'autre n'est pas déployable.



## Les quatre pièges d'évaluation à éviter (spécifique microfinance)

Un jury de la CIF juge une gestion du risque, pas une prouesse de data science. Quatre pièges
mettraient en péril le capital des coopératives, et il faut savoir les déjouer explicitement.

| Piège | Danger | Parade |
|---|---|---|
| **Accuracy globale** | À 7-12 % de défaut, un modèle qui accorde tout atteint 90 % d'exactitude et ruine l'IMF | Interdire le mot devant le jury. AUPRC et taux de détection à la place |
| **ROC-AUC lue naïvement** | La masse des bons clients rend le taux de faux positifs artificiellement minuscule ; on peut afficher 0,92 et être mauvais sur les défauts | Ajouter l'**AUPRC** et le **rappel de la classe défaut** |
| **Seuil à 0,50** | Traite un capital perdu comme un intérêt manqué : aberration financière | Seuil par matrice de coûts (voir `03-scorecard-et-grille.md`), ~0,15 |
| **Évaluation globale non segmentée** | De bons résultats sur les groupements de femmes peuvent masquer un désastre sur l'agricole | Évaluation stratifiée obligatoire, segment par segment |

### Taux de détection (rappel de la classe défaut)

Au-delà de l'AUC, on énonce une phrase que le jury retient : « sur 100 dossiers qui vont
réellement faire défaut, notre modèle en intercepte X %. » On vise **75 à 80 % de détection** au
seuil opérationnel retenu, en assumant le taux de bons clients bloqués en contrepartie (jamais
masqué). Ce taux se lit directement sur la matrice de confusion au seuil de la grille.

### Évaluation stratifiée, avec les segments d'Afrique de l'Ouest

L'interprétabilité de l'EBM permet de vérifier la robustesse **par segment**, et c'est indispensable
parce que les dynamiques de remboursement diffèrent fortement :

- **Crédit agricole** : lié aux campagnes, plus risqué, vital pour la mission CIF.
- **Groupements de femmes** : historiquement d'excellents taux de remboursement.

On rapporte AUC, AUPRC, rappel et taux d'approbation **pour chaque segment** (urbain/rural,
commerce/agriculture, avec/sans groupe). L'exigence : un bon résultat sur un segment ne doit jamais
masquer un mauvais résultat sur un autre, sinon la CIF subit des pertes sectorielles concentrées et
une communauté se retrouve injustement sur-exposée ou pénalisée.

## Courbe de coût et impact financier (métrique de démonstration)

Au-delà des métriques statistiques, on présente l'**impact financier**, seul langage qui parle
vraiment à un jury de microfinance.

- **AUPRC** (aire sous la courbe précision-rappel) en complément de l'AUC : plus informative sur la
  classe minoritaire (les défauts). Repère : un modèle aléatoire a une AUPRC égale au taux de base
  (~0,08) ; viser un multiple net (sur nos données, ~0,22, soit 2,8×).
- **Courbe de coût** : coût total du portefeuille (en FCFA) en fonction du seuil de décision, avec
  le minimum marqué. On montre l'économie réalisée par rapport au seuil naïf 0,50 (voir la matrice de
  coûts dans `03-scorecard-et-grille.md`).
- **Précision / rappel / F1 aux seuils de la grille** : métriques opérationnelles au point de
  fonctionnement choisi, pas en tête (le seuil est un choix métier, pas une propriété du modèle).
  Le F1-macro n'est pas la métrique de tête : il traite les deux classes à poids égal alors que le
  coût d'un défaut manqué et d'un bon refusé sont asymétriques.

Hiérarchie : discrimination sans seuil (AUC, Gini, KS, AUPRC) et calibration en tête ; coût et
métriques opérationnelles au seuil pour l'impact ; jamais l'accuracy.

## Ce qui est présenté au jury

1. Tableau comparatif des trois modèles : AUC, Gini, AUPRC
2. Courbes ROC superposées
3. Courbe de calibration du modèle retenu
4. Gain de la couche solidaire sur la population éligible (segment de groupe)
5. Taux d'approbation et taux de bons refusés à risque constant
6. Fonctions de forme de 3 variables interprétables

Le point 6 est le plus convaincant : montrer la courbe de l'effet de la régularité d'épargne sur
le score démontre visuellement que le modèle est intelligible, ce qu'aucun concurrent utilisant un
modèle opaque ne pourra faire.
