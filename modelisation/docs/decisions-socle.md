# Décisions techniques SOCLE

## Sources vérifiées — 13 septembre 2026

| Sujet | Sources | Conclusion appliquée |
|---|---|---|
| EBM 0.7.8 | [API officielle EBM](https://interpret.ml/docs/python/api/ExplainableBoostingClassifier.html), [guide EBM](https://interpret.ml/docs/ebm.html) | Types `continuous`, `nominal` et liste ordonnée ; `missing="separate"` explicite ; `eval_terms` pour la décomposition. |
| Recherche | [RandomizedSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html), [scoring scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html) | 40 tirages sur plis temporels croissants, sélection par log-loss puis AUPRC. |
| Calibration | [calibration scikit-learn](https://scikit-learn.org/stable/modules/calibration.html), [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) | Platt conserve une transformation affine du logit ; l'isotonique reste un diagnostic, pas le score décomposable. |
| MLflow | [pyfunc](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html), [Model Registry](https://mlflow.org/docs/latest/ml/model-registry/workflow/) | bundle dans un modèle pyfunc, activation par alias `champion-demo`. |
| DVC | [remotes S3](https://dvc.org/doc/user-guide/data-management/remote-storage/amazon-s3), [dvc pull](https://dvc.org/doc/command-reference/pull) | Parquet et bundles dans SeaweedFS S3 ; code et métadonnées seulement dans Git. |
| Déséquilibre | [fit EBM / `sample_weight`](https://interpret.ml/docs/python/api/ExplainableBoostingClassifier.html), [pondération équilibrée scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.utils.class_weight.compute_sample_weight.html) | EBM 0.7.8 accepte `sample_weight`, pas un paramètre `class_weight`. La variante pondérée est comparée temporellement au modèle non pondéré ; aucune sur/sous-extraction ne modifie le Parquet. |

Les APIs et versions sont épinglées dans `pyproject.toml` et son verrou `uv.lock`.

## Décisions métier déjà reçues

- `date_deblocage` remplace une date de demande absente, comme proxy synthétique documenté.
- Le défaut est un retard d'au moins 30 jours ; les retards 15–29 sont exclus de l'entraînement.
- Les résultats d'un crédit (statut, retard, paiement, visite, relance) ne sont jamais une feature de ce même crédit.
- Sexe, situation matrimoniale, âge et segment ne sont pas prédicteurs. `segment` est exclu car il peut révéler `femme_gie`.
- Produit, taux et périodicité exacts sont postérieurs au score. Le taux moyen catalogue sert seulement à estimer la charge de la demande.
- Revenus inconnus : valeur manquante conservée, avec avertissement visible ; aucun refus automatique.
- Garantie brute, nantissement, appel de garantie, GIE et chocs sectoriels sont reportés au modèle enrichi.

## Décisions volontairement différées

1. Les seuils de décision (approbation, revue, refus) ne sont pas appris ni codés dans le SOCLE. Ils seront décidés après lecture des courbes de calibration, coûts métier et capacité de revue.
2. La classification des objets de crédit « divisible / indivisible » n'existe dans aucune source de référence. Elle n'est ni inventée ni utilisée. Le moteur de décision attend une table métier versionnée, avec objet, classe et règle correspondante.
3. Les variables de solidarité et de secteur restent dans le modèle enrichi. Les réponses métier seront consignées dans `questionnaire-modele-enrichi.md` avant toute implémentation.

## Déséquilibre de classes

Le défaut représente environ 8,4 % des lignes entraînables : il est minoritaire, mais pas rare au point de justifier une fabrication de lignes par SMOTE ou un sous-échantillonnage des bons payeurs. Le flux conserve donc la prévalence réelle du simulateur et compare :

1. EBM non pondéré, référence pour une probabilité naturellement calibrée ;
2. même EBM avec `sample_weight="balanced"` calculé dans chaque pli d'entraînement uniquement ;
3. calibration Platt sur 2023 pour la variante retenue ;
4. log-loss, AUPRC, rappel, Brier, ECE et stabilité AUC temporelle.

La pondération n'est retenue que si elle améliore le critère principal (log-loss) sans dégrader les portes de calibration. Le rappel seul ne suffit pas : le score doit rester une probabilité exploitable pour la décision humaine. Aucune stratégie de rééchantillonnage n'est appliquée sans décision métier ultérieure.

Les rapports publient la courbe précision-rappel, mais ne retiennent aucun seuil de refus ou d'accord : cet arbitrage dépend des coûts métier et de la capacité de revue. L'alias MLflow `champion-demo` ne peut être posé qu'explicitement après revue humaine des métriques ; l'entraînement enregistre seulement un candidat.
