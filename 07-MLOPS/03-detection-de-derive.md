# Détection de dérive

## Trois types de dérive

| Type | Définition | Détection |
|---|---|---|
| **Dérive des variables** | La distribution des entrées change | PSI par variable |
| **Dérive de la cible** | Le taux de défaut change | Suivi du taux observé |
| **Dérive du concept** | La relation entrées / cible change | Chute de performance à distribution stable |

La troisième est la plus dangereuse et la plus lente à détecter, puisqu'elle exige d'attendre que
les crédits arrivent à échéance.

## Indice de stabilité de population (PSI)

```
PSI = Σ (part_actuelle − part_reference) × ln(part_actuelle / part_reference)
```

Calculé sur 10 déciles définis sur le jeu de référence.

| PSI | Interprétation | Action |
|---|---|---|
| < 0,10 | Stable | Aucune |
| 0,10 – 0,25 | Dérive modérée | Surveillance renforcée |
| > 0,25 | Dérive marquée | Investigation, réentraînement probable |

Le PSI est calculé sur chaque variable **et** sur la distribution des scores. Une dérive du score
sans dérive des variables signale un problème de modèle, pas de population.

## Fréquence

| Contrôle | Fréquence |
|---|---|
| PSI des variables | Hebdomadaire |
| PSI des scores | Hebdomadaire |
| Taux d'approbation par tranche | Hebdomadaire |
| Taux de défaut observé | Mensuel, sur cohortes matures |
| Performance sur cohorte échue | Trimestriel |

## Le décalage temporel, difficulté propre au crédit

On ne connaît la vérité qu'après la vie du crédit. Un crédit de 12 mois octroyé aujourd'hui ne
révèle son issue que dans un an.

**Conséquences pratiques :**

1. La surveillance de performance porte sur des cohortes **matures**, jamais sur les scorings
   récents.
2. Des signaux avancés sont suivis : taux d'impayé à 30 jours sur les trois premières échéances.
   Imparfait, mais disponible rapidement.
3. Le réentraînement suit un rythme annuel, pas mensuel. Réentraîner trop souvent sur des cohortes
   immatures dégrade le modèle.

Ce point est un excellent sujet de discussion avec un mentor : il montre qu'on a compris la
différence entre le scoring de crédit et un problème de ML classique.

## Outil

**Evidently** pour les rapports de dérive. Génère des rapports HTML lisibles, s'intègre au batch,
open source, auto-hébergeable.

Alternative si l'intégration pose problème : calcul manuel du PSI, qui tient en une trentaine de
lignes. Ne pas se bloquer sur un outil pour une formule simple.

## Alertes

| Condition | Niveau |
|---|---|
| PSI d'une variable > 0,25 | Avertissement |
| PSI du score > 0,25 | Alerte |
| Taux d'approbation dévié de plus de 10 points | Alerte |
| Taux de bascule en mode socle > 60 % | Avertissement — la couche solidaire se dégrade |
| Aucun rafraîchissement du feature store depuis 7 jours | Alerte |

## Périmètre hackathon

**P2.** Ce qui compte pour les 72 heures : que l'architecture le permette et que ce soit
documenté. Une démonstration possible et peu coûteuse : appliquer le modèle à un jeu volontairement
décalé (par exemple la population rurale uniquement) et montrer le PSI se dégrader. C'est
convaincant en trente secondes et cela démontre une maturité MLOps rare dans un hackathon.
