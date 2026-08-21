# Formule cible du crédit progressif — à activer quand le modèle EBM réel existe

## Statut

**Proposition documentée, non implémentée.** Ce fichier fixe la formule vers laquelle
`backend/solida/domain/rules/progressif.py` doit évoluer une fois qu'un modèle EBM réel
(entraîné, calibré) remplace `ModeleConstant`. Tant que ce n'est pas le cas, **ne pas coder cette
formule** : `_modulation_risque` actuel reçoit une probabilité fixe (`ModeleConstant`, 0,09 pour
tout le monde), donc toute formule pondérée par `S_EBM` serait, en l'état, un habillage sans
substance — voir la section « Ce qu'il faut avoir en place avant d'implémenter ».

Ce document consolide une discussion en plusieurs échanges (comparaison de deux formules,
synthèse, cas d'amorçage du premier prêt). Le contenu ci-dessous reprend les formules telles que
discutées, **corrigées** aux endroits indiqués explicitement en fin de document — rien n'est
changé silencieusement.

## 1. Formule maîtresse

$$L_{N+1} = \max \Big( L_{min}, \; \min \big( M \cdot (1 + \delta_N), \; L_{cap}, \; L_{max}, \; D \big) \Big)$$

> **Correction apportée** : le terme $D$ (montant demandé par le sociétaire) a été rajouté dans
> le $\min(\cdot)$. Sans lui, la formule pourrait recommander plus que ce qui a été demandé — ce
> que fait la formule actuellement en production (`min(base·modulation, plafond_produit, D)`,
> `progressif.py:58-62`) et qu'aucune version de la proposition discutée n'incluait. Recommander
> plus que le montant demandé n'a pas de sens métier (un octroi n'est pas une offre non
> sollicitée) — voir section « Corrections apportées » pour le détail.

## 2. L'ancre de capacité prouvée ($M$)

$M$ = montant maximum historiquement remboursé avec succès par le sociétaire — **pas** le dernier
prêt $L_N$. Reprend le choix déjà fait par la formule actuelle (`progressif.py:54`, variable $M$
dans `formules.tex` section 6) : plus conservateur, une ancre sur une capacité *prouvée* plutôt
que sur le dernier montant décaissé (qui peut avoir été lui-même surdimensionné).

## 3. Le taux de variation lissé ($\delta_N$)

$$\delta_N = \begin{cases}
k_{max} \cdot S_{EBM} & \text{si } P_N = 1 \quad \text{(Remboursement parfait)} \\
-\beta \cdot (1 - S_{EBM}) \cdot (1 - P_N) & \text{si } 0 < P_N < 1 \quad \text{(Retard léger, lissé)} \\
-\alpha \cdot (2 - S_{EBM}) & \text{si } P_N = 0 \quad \text{(Retard grave, > 30 jours)}
\end{cases}$$

- **$P_N = 1$ (parfait)** : croissance positive, bornée par $k_{max}$, modulée par la confiance
  du modèle.
- **$0 < P_N < 1$ (retard léger)** : pénalité proportionnelle à la gravité du retard $(1-P_N)$,
  amortie si le profil global ($S_{EBM}$) est solide. Élimine l'effet de falaise identifié dans
  la première version discutée (1 jour de retard ≠ 29 jours de retard).
- **$P_N = 0$ (retard grave)** : pénalité sévère mais toujours modulée par $S_{EBM}$, jamais
  ignorée comme dans la version à paliers fixes.

**Discontinuité résiduelle, volontaire et distincte de la falaise corrigée** : au passage de
"presque parfait" ($P_N \to 1^-$, $\delta_N \to 0$) à "parfait" ($P_N = 1$, $\delta_N =
k_{max}\cdot S_{EBM}$), il reste un saut. C'est différent du problème initial : "aucun jour de
retard" est un fait binaire, objectivement vérifiable — pas un point arbitraire sur un continuum
comme l'était la frontière retard léger/grave. Assumé, pas une falaise oubliée.

**$S_{EBM}$** : score de confiance $\in [0,1]$, $1$ = risque minimal. À définir comme
$S_{EBM} = 1 - p$ où $p$ = `ProbabiliteDefaut` déjà produite par le port `ModeleScoring` — aucun
nouveau concept à créer, juste un remappage du type existant.

**$P_N$** : jamais défini opérationnellement dans la discussion — à combler avant implémentation.
Proposition cohérente avec le seuil « > 30 jours » déjà utilisé des deux côtés de la formule :
$$P_N = 1 - \min\Big(\frac{\text{jours de retard max observés ce cycle}}{30},\; 1\Big)$​$$
Donne $P_N=1$ à 0 jour de retard, $P_N=0$ à 30 jours ou plus, linéaire entre les deux. Point à
valider avec le comité de crédit, pas une valeur mesurée.

## 4. Les garde-fous

### $L_{cap}$ — plafond de capacité (DSR)

$$L_{cap} = \text{DSR}_{max} \cdot R \cdot \frac{(1+i)^{D_{N+1}} - 1}{i \cdot (1+i)^{D_{N+1}}}$$

> **Correction apportée** : la formule discutée était
> $L_{cap} = \dfrac{R \cdot \text{DSR}_{max} \cdot D_{N+1}}{1 + i \cdot D_{N+1}}$, qui est l'inverse
> d'un amortissement **à taux forfaitaire** (mensualité = capital + intérêt simple, répartis à
> parts égales). Or `backend/solida/domain/rules/echeance.py::calculer_echeance_mensuelle`
> utilise explicitement l'**amortissement à annuité constante** (intérêt dégressif sur le capital
> restant dû) — méthode que le code documente comme imposée par la réglementation BCEAO pour le
> TEG/TAEG dans l'UEMOA et effectivement appliquée par les coopératives togolaises. Les deux
> méthodes ne donnent pas le même $L_{cap}$ pour un même $R$/$i$/$D$ (vérifié numériquement :
> pour $i=1{,}5\%$/mois, $n=6$, la mensualité forfaitaire est \~3,5 % plus élevée que la
> mensualité à annuité constante pour un même capital — donc un $L_{cap}$ dérivé du forfaitaire
> serait inutilement plus bas que ce que le produit réellement vendu autoriserait). La formule
> ci-dessus est l'inverse exact de `calculer_echeance_mensuelle` : injecter $L_{cap}$ dedans
> reproduit exactement $\text{DSR}_{max}\cdot R$ comme mensualité — invariant vérifiable par un
> test le jour de l'implémentation.

### $L_{max}$ et $L_{min}$

Inchangés : $L_{max}$ = plafond réglementaire/produit (équivalent de `plafond_produit`,
`progressif.py`), $L_{min}$ = plancher opérationnel (équivalent de `montant_plancher`, déjà
50 000 FCFA dans le système actuel — pas besoin d'une nouvelle valeur).

## 5. Amorçage — premier prêt ($N=1$, pas d'historique)

$$M_{effectif} = \begin{cases}
\text{Max historique remboursé} & \text{si } N \ge 2 \\
\min\big(L_{entrée}, \; \gamma \cdot L_{cap}\big) \cdot \big(0{,}5 + 0{,}5 \cdot S_{EBM}\big) & \text{si } N = 1
\end{cases}$$

$L_{entrée}$ = plafond de démarrage produit, $\gamma$ = décote de sécurité (ex. $0{,}5$),
modulateur borné $[0{,}5,\,1{,}0]$ selon $S_{EBM}$ à l'octroi.

> ⚠️ **Conflit avec une politique déjà documentée, à trancher explicitement** :
> `03-MODELE/04-cascade-et-cold-start.md` (« Traitement du primo-emprunteur ») fixe aujourd'hui
> le plafond du premier prêt à **`plafond_primo_emprunteur`, une constante fixe unique**, sans
> modulation par $S_{EBM}$ ni décote sur $L_{cap}$. Cette section propose de remplacer ce
> traitement fixe par une formule modulée. **Ce fichier ne modifie pas
> `04-cascade-et-cold-start.md`** (dossier de référence protégé) : c'est une proposition
> d'évolution à faire arbitrer par le comité de crédit, pas un changement déjà acté. Tant que
> l'arbitrage n'est pas fait, la politique actuelle (plafond fixe) reste en vigueur.
> **Correction/clarification** : $L_{entrée}$ n'est pas une nouvelle constante à inventer — c'est
> exactement `plafond_primo_emprunteur` (150 000 FCFA aujourd'hui), déjà dans
> `ParametresProgressif`. Pas de doublon à créer.

## 6. Projection au prochain cycle — remplace `calculer_trajectoire`

`calculer_trajectoire` (`progressif.py:142-161`) affiche aujourd'hui un « Palier suivant
accessible » indicatif, à profil de risque inchangé. Cette section fixe sa version cohérente
avec la nouvelle formule maîtresse — elle n'existait pas dans la discussion d'origine, ajoutée
ici après recherche dédiée (voir justification).

$$\text{palier}_{N+2} = \min\Big(L_{N+1} \cdot (1 + k_{max} \cdot S_{EBM}),\; L_{cap}^{\text{projeté}},\; L_{max}\Big)$$

- **Ancre : $L_{N+1}$**, le montant qui vient d'être décidé pour la demande d'aujourd'hui — pas
  $M$. Cohérent avec la formule actuelle (`montant_recommandé × c × modulation`,
  `formules.tex` section 7) : si le cycle en cours se passe bien, $M$ deviendra lui-même
  $L_{N+1}$ au cycle suivant — projeter depuis $L_{N+1}$ revient à projeter depuis le futur $M$.
- **Uniquement le meilleur cas ($P_{N+1}=1$)**, $S_{EBM}$ gelé sur la valeur connue aujourd'hui.
  Jamais les branches « retard léger/grave » de $\delta_N$ : on ne peut pas savoir comment se
  passera un cycle qui n'a pas commencé. Reprend le principe déjà écrit dans `formules.tex`
  (« modulation gelée sur la probabilité connue aujourd'hui »), appliqué à la nouvelle formule.
- **$L_{cap}^{\text{projeté}}$** : même formule DSR corrigée que la section 4, calculée avec la
  durée $D_{N+1}$ **du cycle en cours** comme hypothèse pour le cycle suivant — la vraie durée du
  prochain prêt n'est pas encore connue. **Cette hypothèse doit être énoncée explicitement à
  l'écran** (ex. « en supposant une durée similaire au prêt actuel »), pas seulement dans le
  calcul.
- **Pas de terme $D$** : il n'y a pas de montant demandé pour un cycle qui n'a pas encore de
  demande.
- **$\text{nb\_cycles}$ reste à $1$**, inchangé.

### Pourquoi ce choix (recherche faite, protocole CLAUDE.md §2)

`formules.tex` (section 7) justifie déjà $\text{nb\_cycles}=1$ en citant les *Guidelines for
Establishing and Operating Grameen-Style Microcredit Programs* (Grameen Foundation) : aucune
institution sérieuse ne pré-calcule ni ne garantit un plafond à plusieurs cycles d'écart, chaque
renouvellement est réévalué au moment où il a lieu — jamais promis à l'avance (« *Does not give
any false hope nor lies to members* »). Recherche complémentaire faite pour cette section :
un précédent réglementaire concret existe pour ce risque exact — la FTC (États-Unis) a obtenu de
Credit Karma un règlement de 3 M\$ en 2022 pour avoir affiché des « pré-approbations » qui n'en
étaient pas réellement (une part significative des utilisateurs « pré-approuvés » se voyaient
ensuite refuser le crédit par le prêteur réel). Conséquence directe pour cette section : la
projection doit rester structurellement impossible à confondre avec un engagement — d'où le
choix du meilleur cas seul (jamais une fourchette qui pourrait laisser croire à une évaluation
fine du risque futur) et l'hypothèse de durée énoncée explicitement plutôt que cachée dans le
calcul.

**Gap identifié, non corrigé ici** : `frontend/components/solida/ResultatScoringVue.tsx:248`
affiche aujourd'hui seulement « Palier suivant accessible » / « Prochain cycle », sans mention
« indicatif », « non garanti » ou « si remboursement parfait ». Vu ce qui précède, cette mention
devrait être ajoutée à l'écran le jour de l'implémentation — changement frontend distinct, non
fait dans ce document.

### Clarification — seuil de 30 jours ($\delta_N$) vs seuil de défaut du modèle (90 jours)

`01-principes-modelisation.md` définit le défaut du modèle à > 90 jours de retard (variable
cible d'entraînement), alors que $P_N$ (section 3) utilise 30 jours comme seuil « retard grave ».
**Vérifié : ce n'est pas une incohérence.** PAR30 (30 jours) et PAR90 (90 jours) sont deux
métriques standard et distinctes du secteur microfinance : PAR30 sert de signal d'alerte précoce
(décision opérationnelle, comme le dimensionnement du prêt suivant), PAR90 sert à la
classification statistique du défaut pour l'entraînement du modèle — une hausse de PAR30 précède
généralement une hausse de PAR90 de 2 à 3 mois. Utiliser 30 jours pour $P_N$ et 90 jours pour la
cible du modèle est cohérent avec la pratique du secteur, pas une erreur à harmoniser.

## 7. Paramètres — aucun n'est calibré, tous à trancher par rétro-test

| Paramètre | Valeur discutée | Statut |
|---|---|---|
| $k_{max}$ | 0,30 | Exemple, à valider par Victoire selon les grilles tarifaires locales |
| $\beta$ | 0,20 | Exemple, non mesuré |
| $\alpha$ | 0,25 | Exemple, non mesuré |
| $\gamma$ | 0,50 | Exemple, non mesuré |
| Modulateur plancher (amorçage) | 0,5 | Exemple, non mesuré |
| $\text{DSR}_{max}$ | 0,33 | Convention internationale largement répandue — **aucun mandat BCEAO/UEMOA retrouvé qui fixe ce chiffre pour la microfinance** (recherche faite, voir échange précédent). Point de départ assumé, pas une règle togolaise. |

Même statut que toutes les constantes actuelles du crédit progressif
(`docs/backend/03-decisions-provisoires-a-revoir.md`, section « Paramètres du crédit
progressif ») : point de départ ajustable par la coopérative, pas une vérité mesurée.

## 8. Ce qu'il faut avoir en place avant d'implémenter

1. **Un modèle EBM réel entraîné et calibré**, remplaçant `ModeleConstant`. Sans ça, $S_{EBM}$
   (défini comme $1-p$) est constant pour tout le monde et la formule ne module rien — exactement
   la même limite que la formule actuelle aujourd'hui (voir section « Statut »).
2. **Une définition opérationnelle de $P_N$** à partir des jours de retard réels (proposition
   section 3, à valider).
3. **Un arbitrage sur $P_N=0$ (retard grave)** : cette formule suppose que le sociétaire reste
   éligible à un nouveau prêt (réduit). Faut-il plutôt un blocage total (inéligibilité, comme le
   fait déjà `SurEndettement` pour un crédit en cours) plutôt qu'un prêt réduit ? Pas tranché ici.
4. **Rétro-test sur historique réel de décisions** pour calibrer $k_{max}$, $\beta$, $\alpha$,
   $\gamma$ — aucun des chiffres ci-dessus n'est mesuré.
5. **Arbitrage explicite sur la section 5** (amorçage) : remplace-t-on
   `04-cascade-et-cold-start.md` ou coexiste-t-il avec le plafond fixe actuel pour certains
   produits ?
6. **Un test d'invariant** vérifiant que $L_{cap}$ (section 4) réinjecté dans
   `calculer_echeance_mensuelle` redonne exactement $\text{DSR}_{max}\cdot R$.
7. **Un ajustement d'affichage frontend** (`ResultatScoringVue.tsx`) pour que le palier projeté
   (section 6) porte une mention explicite « indicatif, non garanti » à l'écran — pas seulement
   dans le code.

## 9. Exemples numériques (repris tels quels, arithmétique vérifiée)

**Cycle en cours, retard léger** : $M=400\,000$, $P_N=0{,}80$, $S_{EBM}=0{,}90$, $L_{cap}=550\,000$
(donné) → $\delta_N = -0{,}20 \times 0{,}10 \times 0{,}20 = -0{,}004$ →
$L_{N+1} = \max(50\,000,\min(398\,400,\,550\,000,\,5\,000\,000)) = 398\,400$ FCFA. *(Le terme $D$
manquant dans l'original ne change pas ce résultat tant que $D \geq 398\,400$ — non précisé dans
l'exemple.)*

**Amorçage, premier prêt** : $M=0$, $L_{cap}=300\,000$ (donné), $L_{entrée}=100\,000$,
$\gamma=0{,}5$, $S_{EBM}=0{,}80$ → base $=\min(100\,000,\,150\,000)=100\,000$ →
$M_{effectif} = 100\,000 \times 0{,}90 = 90\,000$ → $L_1 = 90\,000$ FCFA. Arithmétique vérifiée,
correcte.

**Projection au prochain cycle** (nouvel exemple, section 6) : reprenons la décision du premier
exemple, $L_{N+1}=398\,400$ FCFA, $S_{EBM}=0{,}90$, $k_{max}=0{,}30$, $L_{cap}^{\text{projeté}}$
supposé identique (durée assumée inchangée) $=550\,000$ →
$\text{palier}_{N+2} = \min(398\,400 \times 1{,}27,\; 550\,000,\; 5\,000\,000) =
\min(505\,968,\; 550\,000,\; 5\,000\,000) = 505\,968$ FCFA, affiché comme *« jusqu'à ~506 000
FCFA si le prochain cycle est remboursé sans retard, à durée similaire — non garanti »*.

## 10. Corrections apportées — résumé

| Élément | Discuté | Corrigé ici | Pourquoi |
|---|---|---|---|
| Terme $D$ | Absent du $\min(\cdot)$ maître | Rajouté | Sans lui, on peut recommander plus que demandé ; la formule actuelle en production l'inclut déjà |
| $L_{cap}$ | Dérivé d'un amortissement forfaitaire | Dérivé de l'amortissement à annuité constante (inverse exact de `calculer_echeance_mensuelle`) | Incohérence avec la méthode que le code utilise déjà et documente comme imposée par la BCEAO |
| $L_{entrée}$ | Présenté comme une valeur d'exemple isolée | Identifié comme `plafond_primo_emprunteur`, déjà existant | Éviter un doublon de constante |
| Section 5 (amorçage) | Présentée comme la formule à suivre | Marquée en conflit avec `04-cascade-et-cold-start.md`, arbitrage requis | Dossier de référence protégé, pas modifiable silencieusement |
| $P_N=0$ | Traité comme prêt réduit systématiquement | Marqué comme arbitrage ouvert (blocage total vs réduction) | Pas tranché dans la discussion |
| $P_N$ | Jamais défini à partir d'une donnée observable | Définition proposée (jours de retard / 30) | Nécessaire pour être implémentable |
| `calculer_trajectoire` | Absent de la discussion | Section 6 ajoutée (ancre $L_{N+1}$, meilleur cas seul, $L_{cap}$ projeté avec hypothèse de durée explicite) | La formule maîtresse ne peut pas changer sans que la projection au cycle suivant reste cohérente avec elle |
| Seuil 30j ($P_N$) vs 90j (défaut modèle) | Semblait incohérent | Clarifié : PAR30 (alerte précoce) et PAR90 (défaut statistique) sont deux métriques standard distinctes du secteur, pas une erreur | Recherche faite, pas d'harmonisation nécessaire |

Le reste (formule maîtresse, $\delta_N$, structure de $M_{effectif}$, tous les paramètres
numériques d'exemple) est repris à l'identique de la discussion — aucune autre correction jugée
nécessaire.
