# Éthique de la décision automatisée

Ces engagements figurent dans la note de présentation remise au jury. Ils doivent être vrais dans
le code, pas seulement dans le document.

## 1. Exclusion des variables sensibles

**Exclues du modèle :** sexe, appartenance ethnique, appartenance religieuse, opinion politique,
état de santé, situation matrimoniale (par prudence).

**Générées dans CORE-SIM, mais retirées avant l'entraînement.** Elles servent uniquement au
contrôle a posteriori de non-discrimination.

**Mise en œuvre :** une liste de variables interdites est définie dans la configuration. Un test
automatique vérifie qu'aucune n'apparaît dans les variables du modèle entraîné. Si l'une apparaît,
**l'entraînement échoue**, il ne se contente pas d'avertir.

## 2. Contrôle des substituts

Exclure une variable ne suffit pas : une autre peut en tenir lieu. Le secteur d'activité, par
exemple, est corrélé au sexe dans le commerce de détail.

**Contrôle appliqué :** après entraînement, mesure de l'écart de taux d'approbation entre groupes
à score comparable. Un écart supérieur à 5 points déclenche une revue de la variable suspecte.

Cette revue est **humaine**. On ne retire pas automatiquement une variable corrélée : le secteur
d'activité a une valeur prédictive légitime. On documente l'arbitrage.

## 3. Explicabilité de droit

Aucune décision n'est rendue sans facteurs explicatifs restituables au sociétaire. La fiche de
justification n'est pas une option de confort, c'est une condition de fonctionnement.

Un scoring dont la décomposition en points échoue est **rejeté**, pas rendu sans explication.

## 4. Décision humaine finale

SOLIDA formule une **recommandation**. L'agent et le comité conservent le pouvoir de décision et
la faculté de motiver un écart.

**Mise en œuvre :** l'écart entre recommandation et décision finale est enregistré, avec son motif.
Il n'est pas traité comme une anomalie mais comme une donnée de pilotage. Un taux d'écart élevé
peut signaler un modèle mal calibré autant qu'un agent réfractaire.

L'interface n'affiche jamais le mot « décision » seul pour désigner la sortie du système : c'est
toujours « recommandation ».

## 5. Souveraineté des données

Les données restent la propriété de la coopérative et ne quittent pas son périmètre.

**Mise en œuvre :** aucun appel sortant vers un service tiers avec des données de sociétaire.
Aucune télémétrie contenant des données métier. Les modèles sont entraînés localement. Cette
règle est vérifiée par une revue des dépendances réseau.

## 6. Droit à la contestation

Le sociétaire doit pouvoir contester. Cela suppose que la décision soit rejouable des mois plus
tard, à l'identique, avec le modèle et la grille de l'époque.

**Mise en œuvre :** `decision_scoring` conserve entrées, features, versions et résultat. Une
fonction de rejeu permet de reproduire une décision passée. Sans cette capacité, le droit à la
contestation est théorique.

## 7. Ce que nous refusons explicitement

| Refusé | Motif |
|---|---|
| Refus automatique sans intervention humaine | La décision reste humaine |
| Score affiché sans justification | Contraire à l'engagement d'explicabilité |
| Utilisation du score à d'autres fins que l'octroi | Le score n'est pas une note de moralité |
| Partage du score avec des tiers | Souveraineté |
| Modèle opaque, même plus performant | L'explicabilité prime sur la performance |

## 8. Mention obligatoire

Toute fiche remise à un sociétaire porte :

> « Ce document présente les éléments ayant fondé la recommandation du système d'aide à la décision.
> La décision finale relève de l'agent de crédit et du comité de crédit de la coopérative. »
