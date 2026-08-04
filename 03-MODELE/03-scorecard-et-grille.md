# De la probabilité au score, et du score à la décision

## Chaîne complète

```
features ──► modèle ──► p (probabilité de défaut)
                          │
                          ▼
                    calibration
                          │
                          ▼
              log-odds = ln((1 − p) / p)
                          │
                          ▼
        Score = Offset + Factor × log-odds
                          │
                          ├──► décomposition en points
                          │
                          ▼
                    grille de décision
                          │
                          ▼
              tranche + montant recommandé
```

## Mise à l'échelle

```
Factor = PDO / ln(2)
Offset = Score_ref − Factor × ln(odds_ref)
```

**Paramètres retenus, tous dans la configuration :**

| Paramètre | Valeur | Signification |
|---|---|---|
| `PDO` | 20 | Points doublant le rapport bons / mauvais |
| `Score_ref` | 600 | Score de référence |
| `odds_ref` | 50 | Rapport de référence : 50 bons pour 1 mauvais |
| `score_min` | 300 | Borne basse |
| `score_max` | 850 | Borne haute |

Valeurs dérivées : `Factor = 28,854`, `Offset = 487,10`.

Orientation : **score élevé = risque faible**, convention bancaire. Le ratio est donc
`(1 − p) / p` et non l'inverse.

## Décomposition exacte en points

L'EBM s'écrit :

```
log-odds = β₀ + Σ f_j(x_j) + Σ f_jk(x_j, x_k)
```

La transformation en score étant affine en log-odds :

```
points_j = Factor × f_j(x_j)
points_de_base = Offset + Factor × β₀
Score = points_de_base + Σ points_j
```

**Invariant vérifié par un test à chaque scoring :**

```
| points_de_base + Σ points_j − Score | < 1
```

Si cet invariant échoue, le scoring est rejeté et une erreur est journalisée. Une fiche de
justification dont les points ne somment pas au score détruirait toute la crédibilité du produit
devant un auditeur.

**Traitement des interactions :** les termes d'interaction `f_jk` sont répartis à parts égales
entre les deux variables concernées, avec mention dans le catalogue. Alternative : les afficher
comme une ligne dédiée « Interaction entre X et Y ». **Décision : répartition à parts égales**,
plus lisible pour un agent, moins juste conceptuellement — arbitrage assumé et documenté.

## Calibration

La transformation n'a de sens que si `p` est calibrée. Le boosting produit souvent des
probabilités décalées.

| Étape | Traitement |
|---|---|
| Diagnostic | Courbe de calibration en 10 déciles, Brier score |
| Correction | Régression isotonique si l'écart est marqué, sinon Platt scaling |
| Vérification | Recalcul de la courbe après correction |
| Blocage | Un modèle dont la calibration reste hors tolérance **n'est pas promu en production** |

La calibration est apprise sur le jeu de validation, jamais sur le jeu d'entraînement.

## Grille de décision

**Mécanisme** (aligné sur `simulateur/decision.py`, qui sert de prototype pour la forme du calcul) :
les seuils se calculent à partir de la matrice de coûts, en probabilité, pas comme des points de
score fixés arbitrairement à l'avance :

```
seuil_economique = marge / (marge + LGD)
accord      : p < 0,6 × seuil_economique
vigilance   : p < seuil_economique          (Accord sous condition)
examen      : p < 1,6 × seuil_economique    (Comité de crédit)
sinon       : Défavorable (Refus)
```

Ces probabilités se traduisent ensuite en score par la même transformation PDO que ci-dessus, pour
rester affichables sous forme de score.

**Mais les seuils ne sont pas un choix technique.** `marge`, `LGD` et les multiplicateurs de zone
(0,6 / 1 / 1,6) traduisent l'arbitrage entre taux d'approbation et risque accepté, qui **appartient
à la coopérative**, pas au code. Les valeurs de `decision.py` (`marge = 0,15`, `LGD = 0,75`) sont un
point de départ pour construire et tester la mécanique — pas la vérité finale. L'écran E8 permet à
la coopérative de les ajuster en visualisant l'effet sur l'historique, et le calibrage définitif
dépend aussi du modèle réellement entraîné (calibration de `p`, voir plus haut) : une partie de
cette décision **se prend au moment du hackathon**, pas avant.

## Plafond progressif

Le montant recommandé est ensuite borné par la règle de crédit progressif. Le mécanisme suit la
forme de `simulateur/decision.py` — il module le plafond par le niveau de risque, pas seulement par
l'historique — mais ses paramètres restent, de la même façon, un réglage de la coopérative :

```
base       = max(montant_max_rembourse × coefficient_progression, montant_plancher)
modulation = clip(1,3 − 2 × p, 0,4, 1,2)
plafond_progressif = min(base × modulation, plafond_du_produit, montant_demande)
montant_recommande = max(plafond_progressif, montant_plancher)
```

Paramètres par défaut du générateur : `coefficient_progression = 1,5`, `montant_plancher =
50 000 FCFA`, `plafond_du_produit = 3 000 000 FCFA`.

| Paramètre | Défaut |
|---|---|
| `plafond_primo_emprunteur` | 150 000 FCFA |
| `coefficient_progression` | 1,5 |

Cette règle est **déterministe et pure**. Elle est testée sans modèle ni base, et c'est
précisément ce qui permet de la développer avant même que les données existent.

## Versionnage

Toute modification des paramètres de scorecard ou de grille crée une nouvelle `version_grille`.
Chaque décision persiste la version utilisée. Sans cela, aucune décision passée n'est rejouable.

## Seuil de décision optimal par matrice de coûts

C'est l'argument d'impact financier : on ne se contente pas d'un modèle, on montre en FCFA ce qu'il
fait gagner. Dans un problème déséquilibré (7 % de défaut), le seuil naïf de 0,50 est absurde ; le
bon seuil découle du **coût réel** de chaque type d'erreur.

### La matrice de coûts

| Erreur | Ce qui se passe | Coût |
|---|---|---|
| Faux négatif (`C_FN`) | On accorde à un futur défaillant | Perte en capital = **LGD × exposition** |
| Faux positif (`C_FP`) | On refuse un bon client | **Marge nette** perdue sur la vie du prêt |

**Raffinement 1 — LGD, pas 100 %.** La perte en cas de défaut n'est pas tout le capital : la
caution solidaire est appelée, une part des échéances a déjà été payée, il y a du recouvrement. On
utilise une **perte en cas de défaut (LGD)** réaliste, de l'ordre de 60 à 80 %, pas 100 %. De même,
`C_FP` est la **marge nette** perdue (intérêt moins coût de refinancement), pas l'intérêt brut. Ces
deux corrections rendent le seuil défendable devant un financier.

### Le seuil optimal

On refuse dès que le coût espéré de refuser est inférieur à celui d'accorder :
`(1 − p)·C_FP < p·C_FN`, ce qui donne :

$$\text{seuil}^\* = \frac{C_{FP}}{C_{FP} + C_{FN}}$$

Avec LGD = 75 % et marge = 15 % : `seuil* = 0,15 / (0,15 + 0,75) = 0,167`. Le modèle lève donc une
alerte de défaut dès que la probabilité dépasse ~17 %, pas 50 %. C'est ce qui aligne la décision sur
la réalité financière : perdre le capital coûte bien plus que manquer une marge.

**Raffinement 2 — la calibration est un prérequis.** Ce seuil sur `p` n'a de sens que si `p` est
honnête. Un modèle qui dit 0,17 alors que le vrai risque est 0,30 donne un seuil faux. C'est une
raison de plus pour laquelle la calibration (voir plus haut) est centrale. En pratique, le seuil
théorique donne le point de départ, puis on l'ajuste empiriquement sur le jeu de calibration : sur
nos données, le théorique 0,167 et l'optimal empirique 0,142 sont proches, l'écart reflétant la
calibration réelle.

### Connexion à la grille : ce n'est pas un mécanisme séparé

Le seuil optimal est une **probabilité**. On le traduit en **score** par la même transformation
PD → score (formule PDO ci-dessus). Le `seuil*` en probabilité devient donc directement la **borne
accord / refus de la grille**. Autrement dit, la matrice de coûts n'ajoute pas un second système :
elle donne la façon **économiquement fondée** de fixer les seuils de la grille qu'on a déjà, au lieu
de les poser arbitrairement. Le superviseur peut ensuite les ajuster (écran E8), mais il part d'un
point optimal, pas d'un chiffre au doigt mouillé.

**Raffinement 3 — décider sur la perte espérée, pas seulement la PD.** Les coûts sont proportionnels
au montant. Un petit crédit risqué et un gros crédit un peu risqué n'ont pas la même perte espérée
(`PD × LGD × exposition`). La version aboutie classe les dossiers par **perte espérée**, pas par PD
seule. Avec des fractions LGD et marge constantes, le seuil en PD reste constant, mais le **coût
total du portefeuille** se raisonne en montants : c'est ce qu'on présente au jury.

### Impact démontré

Sur le portefeuille de test du générateur (1 885 crédits, 173 M FCFA), passer du seuil naïf 0,50 au
seuil optimal fait **économiser environ 2,4 M FCFA, soit 17 %** du coût des erreurs. C'est le
chiffre à mettre en avant : le modèle ne « prédit » pas, il **économise de l'argent réel**. À
volume constant, ce pourcentage — pas le montant absolu, propre à l'échantillon de test — est ce
qui se transpose à l'échelle d'un portefeuille réel ou du réseau CIF.

### Au-delà du refus : conditions de réexamen actionnables

Quand la décision n'est pas un accord simple, la fiche ne s'arrête pas au verdict : elle liste les
**leviers concrets et vérifiables dans le système** (régularité d'épargne à atteindre, ratio
d'épargne nantie à renforcer, endettement à réduire) que le sociétaire peut activer, ainsi que la
**trajectoire de plafond** accessible s'il rembourse sans incident sur les cycles suivants. Le refus
cesse d'être une porte fermée : il devient un parcours d'éligibilité. Voir
`simulateur/decision.py` dans le dépôt de simulation pour l'implémentation de référence.

### Garde-fous

Le seuil optimal est un **point de départ recommandé**, pas une porte automatique. La décision reste
humaine (agent, comité). Le seuil se surveille par segment pour éviter d'exclure systématiquement une
zone ou un secteur (cohérent avec `06-ethique-et-non-discrimination.md`). Et il se recalcule quand
les coûts réels de l'institution changent (taux d'usure, coût de refinancement).
