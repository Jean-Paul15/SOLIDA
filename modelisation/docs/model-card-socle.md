# Model card — SOCLE EBM

## Usage prévu

Recommandation de risque de défaut à 30 jours pour une demande de microcrédit SOLIDA, à usage de démonstration sur données synthétiques. La décision finale est humaine. Le résultat ne doit jamais être utilisé comme refus autonome.

## Cible et population

Une ligne représente un crédit. `date_deblocage` est la date de référence. La cible est `1` si une échéance atteint 30 jours de retard ou plus, `0` si le retard maximal est au plus 14 jours, et absente pour les cas 15–29 jours ou non encore matures (`date_issue + 90 jours > date_fin`).

## Features

Le catalogue figé contient 20 variables de profil, capacité, épargne et historique antérieur. Types pandas et types EBM sont explicitement déclarés. Les manquants restent manquants ; EBM les traite dans une branche séparée. Aucune variable n'est standardisée, imputée ou encodée en dummy pour EBM.

## Sorties

Le bundle retourne une probabilité de défaut calibrée, une empreinte SHA-256, la version, la signature ordonnée et les contributions en log-odds de « bon remboursement ». Interactions réparties à parts égales entre les deux variables.

## Limites

- Données synthétiques : les métriques ne constituent pas une validation clinique ou commerciale.
- Date de demande absente : le déblocage est un proxy, à remplacer dès que le SI fournit la demande.
- Aucune donnée sectorielle datée ni solidarité exploitable dans le SOCLE.
- Zones : utilisées sous contrôle d'équité ; un écart d'approbation supérieur à 5 points déclenche une revue humaine, pas une suppression automatique.

## Gouvernance

Le champion ne peut être activé qu'après contrôle des métriques (calibration, AUC, AUPRC, courbe précision-rappel, écarts par zone) et revue humaine. L'entraînement ne pose pas lui-même l'alias MLflow : le bundle DVC permet un retour à une version vérifiée pendant cette revue.
