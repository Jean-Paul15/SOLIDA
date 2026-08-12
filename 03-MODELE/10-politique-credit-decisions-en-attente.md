# Politique de crédit — décisions en attente

Ce fichier suit le même statut que `docs/backend/03-decisions-provisoires-a-revoir.md` : ce qui
suit n'est pas tranché, c'est un point de départ documenté pour que l'écran « Politique de
crédit » (E8, `/parametrage/grille`) fonctionne dès maintenant sans présenter de valeurs non
calibrées comme validées.

## Méthodologie de calibrage d'un seuil de décision (recherche externe)

Recherche effectuée le 2026-08-10 (protocole CLAUDE.md §2), deux angles croisés :

- [Cut-Off Score – Open Risk Manual](https://www.openriskmanual.org/wiki/Cut-Off_Score) : un
  cutoff peut être un seuil unique ou multi-paliers (accept / refer / decline — c'est exactement
  la forme accord / vigilance / examen / refus déjà en place dans `03-scorecard-et-grille.md`).
  Son niveau dépend des objectifs métier (taux d'approbation cible, taux de défaut plafond, ou
  optimisation profit/perte), et se détermine **par rétro-test sur données historiques réelles**,
  jamais par une formule générique.
- [CGAP — Due Diligence Guidelines for the Review of Microcredit Loan Portfolios](https://www.cgap.org/sites/default/files/CGAP-Technical-Guide-Due-Diligence-Guidelines-for-the-Review-of-Microcredit-Loan-Portfolios-Dec-2009.pdf) ;
  [CGAP — Scoring: The Next Breakthrough in Microcredit?](https://www.cgap.org/sites/default/files/CGAP-Occasional-Paper-Scoring-The-Next-Breakthrough-in-Microcredit-Jan-2003.pdf) :
  en microfinance, la politique de cutoff reste un arbitrage de gouvernance propre à
  l'institution, cohérent avec des pratiques prudentielles — pas un paramétrage technique livré
  clé en main par un fournisseur de modèle.
- [Fintly — How to Optimize Credit Approval Rates Using Scorecard Cutoff Strategies](https://fintly.co/blog/how-to-optimize-credit-approval-rates-using-scorecard-cutoff-strategies/) :
  confirme la pratique de rétro-test (« back-testing historical loan data to find the exact point
  where the profit from good borrowers outweighs the losses from defaults »).

**Conclusion** : il n'existe pas de mapping numérique « conservateur / équilibré / expansif »
publié et réutilisable tel quel dans le secteur — chaque institution le dérive de son propre
historique. SOLIDA suit déjà la bonne pratique structurelle (zones dérivées d'un seuil économique
`marge / (marge + LGD)`, cf. `03-scorecard-et-grille.md:100-117`) ; ce qui manque, c'est la
calibration propre à la coopérative.

## Statut actuel des paramètres (rappel, détail dans `docs/backend/03-decisions-provisoires-a-revoir.md`)

`marge` = 0,15, `lgd` = 0,75, multiplicateurs de zone accord/vigilance/examen = 0,6 / 1 / 1,6.
Hérités d'un prototype de calcul retiré du dépôt (`09-lecons-prototype-simulateur.md`), pas une
vérité mesurée — point de départ ajustable par le superviseur depuis l'onglet « Seuils » de
l'écran Politique de crédit.

## Décision en attente : préréglages « Prudent / Équilibré / Expansion contrôlée »

L'écran « Politique de crédit » expose la structure d'un sélecteur à trois préréglages nommés,
mais **seul « Équilibré » (= configuration active actuelle) est activable** ; « Prudent » et
« Expansion contrôlée » sont visibles mais désactivés dans l'UI tant que ce qui suit n'est pas
tranché :

- **Ce qui manque** : trois jeux de valeurs numériques (`multiplicateur_accord`,
  `multiplicateur_examen`, éventuellement `marge`/`lgd`) correspondant à trois points de
  fonctionnement distincts (ex. taux d'approbation cible différent, ou taux de défaut plafond
  différent), dérivés par rétro-test sur l'historique réel de décisions.
- **Pourquoi ce n'est pas tranché ici** : `ModeleConstant` (voir
  `docs/backend/03-decisions-provisoires-a-revoir.md`, section « Le modèle lui-même ») renvoie
  aujourd'hui une probabilité de défaut fixe — un rétro-test mené maintenant ne mesurerait rien
  de réel. Le calibrage n'a de sens qu'une fois l'EBM entraîné.
- **Qui tranche** : le responsable risque (rôle `superviseur`), après entraînement et calibration
  du modèle réel, par rétro-test sur l'historique réel de décisions.
- **Attendu** : trois triplets de valeurs, chacun assorti du taux d'approbation et du taux de
  défaut observés en rétro-test, pour remplacer les boutons désactivés par des préréglages
  réellement sélectionnables.

## Décision en attente : seuil d'alerte sur le volume de lecture (recherche/dossier sociétaire)

Le pentest round 3 a démontré qu'un agent légitime peut parcourir tout le fichier de son agence
(paginer `recherche` sur de nombreux termes, puis `dossier` sur chaque résultat) sans qu'aucune
alerte ne se déclenche. Corrigé depuis : `recherche`/`dossier` journalisent IP réelle et
navigateur, et `backend/solida/batch/jobs/detecter_lectures_anormales.py` écrit une alerte
(`alerte_volume_lecture`) au-delà de 100 lectures/heure par acteur — **jamais de blocage
automatique** (voir `docs/backend/07-monitoring-securite.md` pour le détail et le rationnel).
Ce qui reste réellement en attente :

- **Le seuil (100/heure)** est repris de la recommandation du rapport de pentest, pas mesuré sur
  un usage réel — un point de départ, pas une valeur figée.
- **Qui tranche la valeur définitive** : le responsable risque/opérations (rôle `superviseur` ou
  `administrateur`), une fois un volume de lecture normal observé en production (les logs
  `recherche_societaires`/`consultation_dossier` de `journal_audit` fournissent déjà la matière).
- **Attendu** : un ajustement de `SEUIL_LECTURES` dans `detecter_lectures_anormales.py` dérivé de
  cette observation, pas d'une intuition. La réponse à une alerte reste humaine (revue puis,
  si besoin, blocage via `cli_provisionner_comptes bloquer`) — ce point-là n'est pas en attente,
  déjà tranché explicitement pour éviter qu'un seuil automatique ne devienne un vecteur de déni
  de service.

## Périmètre administrateur modèle : confirmé hors SOLIDA

Calibration, validation et publication du modèle restent hors du périmètre applicatif de SOLIDA,
conformément à `docs/backend/05-use-cases-et-routeurs.md:12-13` (écran E9 retiré du périmètre
produit, aucun endpoint dédié). Le rôle `administrateur` opère via l'outillage MLOps externe
(MLflow, tableaux de bord Grafana — voir `07-MLOPS/`), pas depuis une page de l'application
SOLIDA. En conséquence, PDO, score de référence et rapport de référence (`odds_reference`) ne
sont plus édités depuis l'écran Politique de crédit : ils y sont affichés en lecture seule via les
calculs dérivés (seuils résultants), transmis inchangés lors de l'enregistrement d'un nouveau
seuil ou plafond.
