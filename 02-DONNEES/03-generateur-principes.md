# Principes du générateur CORE-SIM

## Règle fondatrice

**Toute la mécanique est dans le code, toutes les valeurs sont dans le YAML.**

Le retour du praticien IMF ne doit modifier **que** le fichier de configuration. Si un ajustement
de proportion oblige à toucher au code Python, la séparation a été mal faite.

## Ordre de génération

L'ordre est contraint par les dépendances. Il n'est pas modifiable arbitrairement.

```
1. Référentiels          agences, agents, produits
2. Sociétaires           profils, adhésions étalées dans le temps
3. Comptes d'épargne     ouverture liée à l'adhésion
4. Groupes de caution    constitution par agence et par zone
5. Appartenances         affectation aux groupes, avec sorties
6. Mouvements d'épargne  simulation mensuelle, avec régularité variable par profil
7. Demandes de crédit    étalées dans le temps, cycles croissants
8. Décisions             accord / refus selon un modèle de décision simulé
9. Crédits               pour les demandes accordées
10. Garanties            selon le type de garantie du produit
11. Échéanciers          calcul déterministe
12. Remboursements       simulation du comportement, génération du défaut
13. Contrôles            module A7
```

## Le point le plus délicat : calibrer sur la réalité, laisser la performance émerger

Un générateur naïf produit des données aléatoires dans lesquelles aucun modèle ne trouve rien.
Un générateur trop simple produit une relation évidente qu'un modèle apprend parfaitement, ce qui
donne une AUC de 0,99 et ridiculise l'équipe devant un jury.

**La méthode retenue n'est pas de viser une AUC, mais de calibrer les mécanismes sur des grandeurs
réelles et de valider la performance qui en émerge.** Cibler une AUC revient à décider le résultat
avant de faire l'expérience — ça se voit, et un jury sectoriel le décèlera.

1. Définir une **propension latente au défaut** par sociétaire, comme somme pondérée de facteurs
   dont l'**amplitude de chacun est un rapport de cotes issu de la littérature empirique du défaut
   en microfinance** (régularité et trajectoire d'épargne, ratio d'endettement, cycle, segment,
   qualité du groupe sur le segment concerné, secteur, zone) — pas des coefficients choisis pour
   obtenir un chiffre.
2. Y ajouter une composante **individuelle non observable** (le générateur la connaît, le modèle
   non), fixée par raisonnement métier sur la part réelle d'aléa en microcrédit (santé, aléa
   commercial, événement familial) — pas ajustée pour atteindre une AUC cible.
3. Caler l'intercept du modèle sur le **taux de défaut réel** du secteur (marginale observable),
   jamais sur une AUC.
4. Tirer le défaut selon cette propension.
5. **Ensuite seulement**, mesurer l'AUC qui émerge et la **valider** contre la fourchette
   documentée du secteur (0,70-0,85 pour du scoring de microcrédit ; au-delà de 0,85-0,88, suspecter
   une variable trop déterministe, comme on suspecterait une fuite ; en dessous de 0,68, des
   mécanismes trop faibles). Si l'AUC sort de la fourchette, on retourne aux mécanismes eux-mêmes
   (leur réalisme, leur richesse), jamais à un paramètre de bruit ajusté pour « corriger » le
   résultat.

Chaque coefficient et chaque grandeur cible doivent être **documentés avec leur source** dans le
rapport de génération (littérature citée ou statistique publique du secteur). C'est ce qui rend le
générateur défendable devant un expert : pas le fait d'atteindre un chiffre, mais le fait que
chaque paramètre soit traçable.

## Le signal solidaire (segment de groupe)

Pour que la couche solidaire démontre son apport, le générateur injecte une **corrélation
intra-groupe réaliste** : les membres d'un même groupe partagent une part de leur propension au
défaut, parce que la responsabilité conjointe rend les défauts corrélés (documenté empiriquement
sur le crédit de groupe en Inde, au Mexique, au Pakistan). L'amplitude de cet effet est calibrée
sur cette littérature, pas ajustée pour produire un gain d'AUC choisi à l'avance.

**L'apport mesuré de la couche solidaire doit être rapporté tel qu'il sort, même s'il est modeste.**
Sur le prototype, il est de l'ordre de quelques millièmes à un centième d'AUC, et il est
probablement **sous-estimé** par le démarrage à froid des groupes synthétiques (peu d'historique
accumulé) — ce qui doit être dit au jury plutôt que masqué en gonflant artificiellement l'effet.

**Ce que nous assumons devant le jury :** nous générons les données, donc nous choisissons les
mécanismes ; la bonne posture n'est pas de cacher ce choix mais de citer ses sources, et d'expliquer
que la validation réelle passe par le rejeu sur données d'une IMF pilote.

## Valeurs manquantes

Injectées volontairement, selon les taux du YAML. Elles ne sont pas aléatoires uniformément :
les dossiers ruraux et les primo-emprunteurs ont plus de champs vides que les dossiers urbains de
cycle 4. C'est ce qu'on observe en pratique, et c'est ce qui oblige le modèle à savoir traiter
l'absence.

## Reproductibilité

| Élément | Règle |
|---|---|
| Graine | Fixée dans le YAML, journalisée dans le rapport |
| Générateur aléatoire | Une instance passée explicitement, jamais de global |
| Sortie | Base + rapport de conformité + copie du YAML utilisé |
| Versionnage | Le YAML est versionné, la base ne l'est jamais |

Deux exécutions avec le même YAML doivent produire des bases identiques au bit près.

## Interdits

| Interdit | Motif |
|---|---|
| Valeur numérique en dur dans le code | Empêche l'ajustement après retour du praticien |
| Générer directement la variable cible sans modèle causal | Produit des données sans structure apprenable |
| Utiliser un jeu de données réel maquillé | Risque juridique et malhonnêteté |
| Générer des noms réels de personnes existantes | Utiliser des générateurs de noms togolais plausibles |
| Faire dépendre le défaut d'une variable exclue du modèle | Créerait un plafond artificiel inexplicable |

## Le choc sectoriel latent (variable dans le temps)

Pour que les variables de conditions sectorielles (voir `03-MODELE/02` et ADR-014) portent un
signal, le générateur doit injecter une **santé de secteur qui varie dans le temps**, de façon
irrégulière. C'est la traduction, dans les données, du fait que les saisons ne sont plus régulières.

**Ce qu'on ne fait surtout pas :** un calendrier fixe où « juin = risque élevé pour l'agriculture ».
Ce serait supposer la régularité que la réalité a perdue, et rendre le signal trivial et faux.

**Ce qu'on fait :** un processus latent par secteur, du type marche autocorrélée (AR(1)), qui monte
et descend au fil des mois sans période fixe. À chaque mois `t` et pour chaque secteur `s`, un état
`sante(s, t)` évolue à partir de `sante(s, t-1)` avec un choc aléatoire, éventuellement avec des
épisodes de dégradation marquée (mauvaise campagne) tirés aléatoirement, pas calés sur un mois.

Ce `sante(s, t)` entre dans la propension latente au défaut d'un crédit décaissé à ce moment dans ce
secteur. Il n'est **pas** donné au modèle : le modèle ne le voit qu'indirectement, à travers les
tendances observées du portefeuille (impayés, épargne) qu'il produit.

**Cibles de calibrage (dans le YAML) :**

| Paramètre | Cible |
|---|---|
| Amplitude du choc sectoriel | Apport de 1 à 3 points d'AUC des variables sectorielles, sur les crédits agricoles |
| Autocorrélation mensuelle | Élevée (0,7 à 0,9) : un secteur qui va mal reste tendu quelques mois |
| Fréquence des épisodes de dégradation | Irrégulière, tirée aléatoirement, jamais périodique |

**Intuition à préserver :** quand un secteur bascule, ça se voit d'abord dans l'épargne (les membres
puisent), puis dans les impayés (les échéances sont manquées). Le générateur doit produire ce
décalage, sinon la variable « dynamique d'épargne » ne serait pas l'indicateur avancé qu'on annonce.
