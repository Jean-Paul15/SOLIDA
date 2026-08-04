# Qualité des données

## Trois niveaux de contrôle

| Niveau | Quand | En cas d'échec |
|---|---|---|
| Structure | À l'ingestion | Rejet du lot |
| Cohérence | Après ingestion | Alerte, ingestion conservée |
| Distribution | Après calcul des features | Alerte, comparaison à la référence |

## Contrôles de structure

Colonnes attendues présentes, types conformes, identifiants non nuls et uniques, encodage UTF-8,
dates parsables, montants entiers positifs.

## Contrôles de cohérence

| Contrôle | Seuil |
|---|---|
| Garanties orphelines | 0 |
| Crédits sans sociétaire | 0 |
| Remboursements antérieurs au déblocage | 0 |
| Somme remboursée > total dû | 0 |
| Groupes vides | alerte si > 5 % |
| Sociétaires sans compte d'épargne | alerte si > 20 % |

## Contrôles de distribution

Comparés à un profil de référence figé lors de la première ingestion validée.

| Indicateur | Seuil d'alerte |
|---|---|
| Taux de valeurs manquantes par colonne | écart > 10 points |
| Médiane des montants | écart > 25 % |
| Taux de défaut | écart > 3 points |
| Part de primo-emprunteurs | écart > 10 points |
| Taille moyenne des groupes | écart > 30 % |

## Traitement des valeurs manquantes

**Principe : ne jamais imputer silencieusement.**

| Variable | Traitement | Signalé à l'agent |
|---|---|---|
| Revenu déclaré | Médiane du secteur et de la zone | Oui, avertissement explicite |
| Charges | Ratio médian appliqué au revenu | Oui |
| Ancienneté d'activité | Médiane du secteur | Non, impact faible |
| Features de la couche solidaire | **Aucune imputation**, bascule en mode socle | Oui, bandeau de mode |
| Historique de crédit absent | Traité comme primo-emprunteur, pas comme donnée manquante | Oui, bandeau de mode |

L'EBM traite nativement les valeurs manquantes comme une modalité. Ce comportement est
**préférable à l'imputation** quand l'absence est elle-même informative — un dossier sans revenu
déclaré n'est pas un dossier au revenu médian, c'est un dossier mal instruit, et c'est une
information.

Décision : imputer uniquement quand l'absence est manifestement un défaut de saisie, laisser
l'absence telle quelle quand elle est structurelle, et **toujours l'afficher**.

## Fuite de données — les trois pièges à éviter

C'est la faute qui produit des résultats brillants en développement et un effondrement en
production. Trois vérifications obligatoires :

1. **Fuite temporelle.** Toutes les features sont calculées à `date_reference` = date de la
   demande, jamais à la date d'aujourd'hui. Les agrégats du groupe sont recalculés à cette date.
2. **Fuite par la cible.** Aucune variable dérivée du remboursement du crédit en cours ne peut
   entrer dans le modèle. Le statut du crédit instruit est interdit en entrée.
3. **Fuite par le groupe.** Le taux de remboursement du groupe ne doit pas inclure le crédit du
   sociétaire évalué, sinon on lui prédit son propre défaut.

Chacune de ces trois vérifications fait l'objet d'un test automatique. Le point 3 est le plus
subtil et le plus facile à manquer.

## Découpage entraînement / validation

**Découpage temporel, jamais aléatoire.** Un découpage aléatoire dans un jeu où les crédits ont
des durées produit une fuite : un crédit dont on connaît la fin se retrouve à cheval.

- Entraînement : demandes antérieures à T−12 mois
- Validation : T−12 à T−6
- Test : T−6 à T, jamais consulté avant l'évaluation finale

Cette découpe imite la réalité : on entraîne sur le passé et on prédit l'avenir.
