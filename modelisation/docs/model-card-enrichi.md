# Model card — modèle enrichi (couche solidaire)

## Usage prévu

Même usage que le SOCLE (recommandation de risque de défaut à 30 jours, décision humaine,
démonstration sur données synthétiques) — mais seulement pour un crédit dont l'emprunteur
officiel est le groupe (garantie `caution_solidaire_gie` + `gie_id` renseigné). Une demande
individuelle n'a aucune variable de groupe et devrait recevoir le SOCLE, pas l'enrichi.

## Cible et population

Identique au SOCLE (`classe_cible`, seuils J+15/J+30, maturité à 90 jours). Le jeu enrichi
contient les mêmes 12 690 crédits ; les 6 variables de groupe sont `null` hors crédit de
groupe et pour tout groupe de moins de 5 membres actifs (`précision.txt` R22).

## Features

20 features SOCLE inchangées + 6 variables de groupe (`FEATURES_GROUPE` dans
`catalogue.py`) : `taille_groupe`, `anciennete_groupe_mois`, `nb_credits_groupe_anterieurs`,
`nb_incidents_groupe_anterieurs`, `max_jours_retard_groupe_6m`,
`nb_cautions_appelees_anterieures`. Les 4 features d'historique individuel
(`nb_incidents_anterieurs`, `max_jours_retard_historique`, `montant_max_rembourse`,
`ratio_montant_historique`) sont recalculées en excluant les échéances enregistrées au
niveau du groupe (5.10) : elles diffèrent du SOCLE sur 987 des 12 690 lignes.

## Comparatif à trois modèles (test ≥ 2024, mêmes lignes)

| Modèle | AUC | Gini | AUPRC | Log-loss | Brier | ECE | Écart décile |
|---|---:|---:|---:|---:|---:|---:|---:|
| Référence logistique | 0,88195 | 0,76391 | 0,66620 | 0,18707 | 0,04935 | 0,01340 | 0,03543 |
| SOCLE | 0,89850 | 0,79700 | 0,69549 | 0,17546 | 0,04660 | 0,01775 | 0,03788 |
| Enrichi | 0,89699 | 0,79398 | 0,68747 | 0,17999 | 0,04712 | 0,01751 | 0,02243 |

Sur le test complet (10 530 individuels + 2 037 crédits de groupe, la plupart sans variable
de groupe exploitable pour l'individuel), l'enrichi ne fait pas mieux que le SOCLE — attendu,
puisque l'écrasante majorité des lignes n'a aucune variable de groupe à exploiter.

## Apport de la couche solidaire (J2-04) — population éligible uniquement

Mesuré sur les seuls crédits de groupe du test (`taille_groupe` non nulle), avec IC 95 %
bootstrap (1 000 tirages, graine 42) :

| Métrique | SOCLE | Enrichi | Δ (enrichi − SOCLE) | IC 95 % |
|---|---:|---:|---:|---|
| AUC | 0,95410 | 0,95433 | +0,00024 | [-0,0049 ; +0,0049] |
| AUPRC | 0,90911 | 0,90973 | +0,00061 | [-0,0115 ; +0,0113] |
| Log-loss | 0,21553 | 0,21556 | +0,00002 | [-0,0201 ; +0,0245] |
| Brier | 0,06331 | 0,06243 | -0,00088 | [-0,0086 ; +0,0071] |
| ECE | 0,04683 | 0,04054 | -0,00629 | [-0,0297 ; +0,0202] |
| Écart max. décile | 0,19658 | 0,10325 | -0,09332 | [-0,2208 ; +0,0923] |

**Effectif : 154 crédits de groupe étiquetés dans le test, 36 défauts.** Très en-deçà du
seuil de fiabilité statistique cité par le terrain (R45, ~8 000 dossiers avant de présenter
une statistique de groupe) : **ce résultat est indicatif, pas une validation**.

**Lecture honnête** : sur la discrimination (AUC, AUPRC, log-loss), l'écart est nul aux
erreurs près — tous les intervalles de confiance couvrent largement zéro. Sur la
calibration (Brier, ECE, écart par décile), l'enrichi est systématiquement un peu meilleur
sur cet échantillon, mais l'intervalle de confiance de l'écart par décile couvre encore
zéro. **Aucune conclusion ferme sur l'apport de la couche solidaire n'est possible avec cet
effectif** ; il faudra réévaluer une fois le volume réel disponible.

## Limites (en plus de celles du SOCLE)

- Aucune donnée de crédit refusé (`decision_historique`/`issue_reelle` absentes des
  parquet) : biais de sélection non corrigé, ni pour le SOCLE ni pour l'enrichi (5.11).
- Caution solidaire : seul le nombre de cautions appelées sur des crédits de groupe déjà
  clos est utilisé ; le montant et le plafond de la caution restent absents (Q12 de
  `précision.txt` sans réponse).
- Épargne du groupe et garantie/nantissement enrichis exclus faute de source datée.
- `nb_cautions_appelees_anterieures` peut sous-compter : `garanties.garantie_appelee` n'est
  pas daté, seul le rattachement à un crédit clos (`date_issue`) est utilisé comme proxy
  de « connu à la référence ».

## Gouvernance

Identique au SOCLE : aucun alias `champion-demo` n'est posé par l'entraînement, revue
humaine requise avant toute promotion. `journaliser_enrichi` ne promeut jamais
automatiquement (voir `mlflow_tracking.py`).
