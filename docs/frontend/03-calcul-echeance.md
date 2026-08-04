# Calcul de l'échéance mensuelle

## Méthode retenue

Amortissement à annuité constante (méthode actuarielle), pas une simple division du montant
par la durée :

```
echeance = montant × [i × (1+i)^n] / [(1+i)^n − 1]
```

où `i` est le taux mensuel et `n` le nombre de mois.

## Pourquoi

- La réglementation BCEAO (zone UEMOA) impose que le coût d'un crédit soit exprimé en Taux Annuel
  Effectif Global (TAEG), calculé par la méthode actuarielle — c'est la même mécanique que
  l'annuité constante. Le plafond (taux d'usure) pour les institutions de microfinance est de 24 %
  l'an depuis le 1er juin 2026 (contre 27 % auparavant).
- Les coopératives d'épargne et de crédit togolaises appliquent un intérêt dégressif sur le capital
  restant dû, pas un taux forfaitaire sur le montant initial (taux flat) : c'est le même principe
  que l'annuité constante, pas la division linéaire initialement implémentée.

Sources : décision de recalibrage du taux d'usure UMOA (communiqués BCEAO, 2026), documentation
pédagogique sur la détermination du TEG/TAEG (École de la microfinance).

## Ce qui reste à trancher

Le taux mensuel exact par produit de crédit n'existe dans aucun document du projet. Le code utilise
une constante de démonstration (`TAUX_MENSUEL_DEMONSTRATION`, 18 %/an) uniquement pour que l'écran
E3 affiche un résultat plausible, largement sous le plafond réglementaire. Cette valeur doit être
remplacée par la table de taux réelle par produit avant toute mise en production.
