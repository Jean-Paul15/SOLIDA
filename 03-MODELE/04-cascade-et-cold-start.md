# Cascade et démarrage à froid

## Le problème

Un modèle qui exigerait un historique de groupe serait inutilisable précisément là où le besoin
est le plus fort : la première demande d'un nouveau sociétaire. Or, dans le calibrage retenu,
**45 % des dossiers sont des primo-emprunteurs**. Un système qui ne les traite pas ne traite pas
le cas majoritaire.

## Logique de sélection

```
SI features_solidaires disponibles ET groupe dispose d'un historique
    ALORS mode = enrichi
          modèle = EBM_enrichi
SINON
    mode = socle_seul
    modèle = EBM_socle
    motif = raison précise de la bascule
```

## Conditions précises du mode enrichi

Les quatre conditions doivent être réunies :

1. Le sociétaire appartient à un groupe à la date de référence.
2. Le groupe compte au moins 3 membres.
3. Le groupe a au moins **3 crédits antérieurs soldés**, hors sociétaire évalué.
4. Les features de la couche solidaire ont moins de 7 jours (`fraicheur_features`).

Si l'une manque, bascule en mode socle, avec un motif explicite.

**Le seuil de 3 crédits antérieurs est un arbitrage.** En dessous, le taux de remboursement du
groupe repose sur trop peu d'observations pour être fiable, et introduirait plus de bruit que de
signal. Ce seuil est paramétrable.

## Motifs de bascule, restitués à l'agent

| Motif interne | Phrase affichée |
|---|---|
| `sans_groupe` | « Ce sociétaire n'appartient à aucun groupe de caution. » |
| `groupe_sans_historique` | « Le groupe de ce sociétaire n'a pas encore d'historique de crédit suffisant. » |
| `groupe_trop_petit` | « Le groupe compte moins de trois membres. » |
| `features_perimees` | « Les données du groupe n'ont pas été actualisées récemment. » |
| `modele_enrichi_indisponible` | « Le calcul étendu est momentanément indisponible. » |

Ces phrases sont **neutres**. Aucune ne suggère un manque du sociétaire ni une panne inquiétante.

## Traitement du primo-emprunteur

Un primo-emprunteur n'est pas un dossier incomplet, c'est un cas normal.

| Aspect | Traitement |
|---|---|
| `nb_credits_anterieurs` | 0, valeur légitime, pas manquante |
| `max_jours_retard_historique` | `null`, pas 0 : aucun retard observé n'est différent d'aucune observation |
| `ratio_montant_historique` | `null` |
| Plafond | `plafond_primo_emprunteur` |
| Message | « Premier crédit. Le montant recommandé applique le principe du crédit progressif. » |

**`null` plutôt que 0** est un point important. Coder « pas d'historique » par 0 retard reviendrait
à accorder au primo-emprunteur le meilleur historique possible.

## Cohérence entre les deux modèles

Les deux modèles partagent la même scorecard, la même grille, les mêmes bornes. Un score de 586
signifie la même chose dans les deux modes.

**Risque à surveiller :** un décalage de calibration entre socle et enrichi produirait un saut de
score au moment où un sociétaire devient éligible au mode enrichi. Un test compare les
distributions de score des deux modèles sur la population éligible aux deux ; un écart de médiane
supérieur à 15 points déclenche une alerte.

## Repli en cas de panne

| Panne | Comportement |
|---|---|
| Modèle enrichi indisponible | Bascule socle, avertissement, scoring rendu |
| Modèle socle indisponible | **Aucun score rendu.** Erreur explicite |
| Feature store indisponible | Aucun score rendu |
| Une feature individuelle absente | Imputation ou modalité manquante, avertissement |

Un score n'est **jamais** rendu sans le socle. Mieux vaut pas de score qu'un score inventé.
