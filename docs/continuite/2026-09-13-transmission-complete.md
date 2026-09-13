# Transmission complète — SOLIDA

## État de reprise

- J1-05 à J1-13 : générateur corrigé et reproductible avec la graine 42.
- J1-14 à J1-21 : SOCLE EBM construit, calibré, explicable, empaqueté et branché au backend.
- Données et bundle : suivis par DVC/SeaweedFS, jamais committés comme binaires Git.
- Modèle enrichi, couche solidaire et moteur de décision : à poursuivre après lecture de ce document et réponse aux questions bloquantes.
- Le dossier `SOLIDA_Documents (2)/` est local, exclu et non requis pour cette reprise.

## Décisions terrain prioritaires

| Sujet | Réponse confirmée | Effet appliqué |
|---|---|---|
| Risque à l'octroi | Défaut, statut, retards, paiements, visites et relances sont postérieurs au déblocage. | Exclus du crédit évalué ; seulement historique réellement observable. |
| Anciennetés | Toujours à la date du crédit / `date_deblocage`. | Générateur et features temporelles. |
| Endettement synthétique | Seuil 0,33, même coefficient avant/après, pente doublée après. | J1-07 configurable. |
| Montant par produit | Aucun montant fixe ou minimum métier par produit. | Le catalogue synthétique porte minimum 0. |
| Maximum réel | 100 000 000 FCFA institutionnels, unique. | Backend sans plafond par produit. |
| Cycles | Pas de coefficient fondé sur le prêt précédent. Client et faisabilité choisissent le montant. | Pas de réduction/projection automatiques. |
| Montant synthétique | Loi log-uniforme 20 000–5 500 000 FCFA. | Simulation seulement, pas règle métier. |
| Périodicité | Hebdomadaire, mensuelle, trimestrielle, semestrielle ou annuelle. | Compatible avec durée ; aucun produit imposé. |
| Échéancier | Échéances constantes, intérêt sur capital restant dû. | Parquet des échéances détaillé. |
| Groupe | Remboursement et retard enregistrés au groupe, non attribués à ses membres. | `niveau_enregistrement="groupe"`. |
| Retard/défaut | Alerte dès J+1 ; défaut à J30. | Cible SOCLE. |
| Épargne | Historique complet dès ouverture, solde initial nul. | Mouvements et soldes mensuels. |
| Nantissement | 10 % à un tiers, libre retiré au déblocage et restitué si soldé. | Garantie du crédit courant exclue du SOCLE. |
| Intérêt épargne | Fourchette annoncée 1–10 %, plafond 10 %, mais règle et fréquence absentes. | Aucun intérêt d'épargne généré. |
| Âge | Renseigné ; sans risque ni refus automatique après 73 ans. | Exclu du SOCLE. |
| Sensibles | Sexe, situation matrimoniale et segment exclus. | Audit d'équité seulement. |
| Non chiffré | Frais, assurance, annulation, régularisation. | Hors génération/modèle. |

## Données disponibles pour l'enrichi

| Source | Ce qui est disponible | Règle de reprise |
|---|---|---|
| `appartenances_gie.parquet` | `gie_id`, sociétaire, entrée, sortie, rôle. | Filtrer active à `date_reference`. |
| `echeances.parquet` | Montants/dates/retards/alerte, niveau, groupe et sociétaire. | Un remboursement groupe reste groupe. |
| `garanties.parquet` | Type, garant, bénéficiaire, montant, engagement, libération, appel. | Ne jamais utiliser la garantie/appel du crédit évalué. |
| Épargne | Mouvements et soldes mensuels depuis l'ouverture. | Utiliser uniquement événements antérieurs. |
| Crédits/produits | Montant, durée, taux appliqué et périodicité. | Produit/taux/périodicité exacts post-score restent exclus du SOCLE. |
| Secteur | Série interne, mais index date absent du Parquet publié. | Interdit tant qu'une date de disponibilité n'est pas fournie. |

## SOCLE EBM : spécification figée

- `date_deblocage` est le proxy de demande synthétique.
- Cible : bon 0–14 jours, indéterminé 15–29, défaut >=30, en cours si `date_issue + 90 jours > 2026-08-01`.
- Entraînable : 9 818 crédits = 8 990 bons et 828 défauts. Non entraînables : 215 indéterminés, 2 657 en cours.
- Splits : train <=2022, validation 2023, test >=2024. Cinq plis temporels croissants ; jamais de split aléatoire.
- Les 20 features autorisées sont figées dans `modelisation/src/solida_modelisation/catalogue.py`.
- Revenu et ratios absents restent `null`. La charge du nouveau crédit est estimée avec montant, durée et taux moyen produit, mais n'est pas une colonne `X` distincte.
- Sont exclus de `X` : GIE, garantie, produit, taux/périodicité exacts, âge, sexe, situation matrimoniale, segment, identifiants, issue du crédit évalué et signaux sectoriels non datés.

## EBM, déséquilibre et métriques

- `interpret-core==0.7.8`, `missing="separate"`, types continus/nominal/ordinal explicites ; aucun dummy, scaling ni imputation du dataset EBM.
- 40 configurations ; choix par log-loss, AUPRC et stabilité temporelle.
- Défaut 8,4 %. EBM accepte `sample_weight`, mais pas `class_weight`. Comparer non pondéré contre poids équilibrés dans chaque pli ; ne pas faire SMOTE ni sous-échantillonnage.
- Non pondéré retenu : log-loss CV 0,17141 contre 0,39952 pondéré. Calibration Platt sur validation 2023 ; isotonique diagnostic uniquement.

| Métrique test | Valeur |
|---|---:|
| AUC | 0,89845 |
| Gini | 0,79690 |
| AUPRC | 0,69471 |
| Log-loss | 0,17869 |
| Brier | 0,04639 |
| ECE | 0,01140 |
| Écart calibration décile | 0,05526 |

L'AUC >0,88 déclenche l'audit renforcé : signature, temporalité, classes et cible sont conformes. Sur données synthétiques, ce niveau exige une revue humaine ; l'alias `champion-demo` n'est pas attribué automatiquement.

## Bundle, backend et MLOps

Le bundle DVC contient modèle, calibrateur, export JSON EBM, catalogue, contributions missing, distributions de référence, manifeste et SHA-256. L'API charge MLflow alias, puis cache vérifié, puis bundle DVC ; elle échoue explicitement sans bundle valide. Le score affiche un avertissement pour revenu manquant et pour données synthétiques.

La couche de décision reste humaine. Les seuils accord/revue/refus, coûts de défaut et de bons refusés ne sont pas décidés. La courbe précision-rappel est livrée pour cet arbitrage.

## Enrichi et moteur de décision : réponses/blocages

| Question | Réponse disponible | État |
|---|---|---|
| GIE daté | Oui : entrée/sortie/rôle. | Prêt techniquement. |
| Remboursement groupe | Oui : groupe seulement. | Prêt, après filtrage temporel. |
| Caution solidaire | Données garanties présentes, règle métier d'éligibilité/plafond/utilisation absente. | Bloqué métier. |
| Nantissement | Libre et historique disponibles ; ne pas employer le courant. | Feature historique possible, choix à valider. |
| Signal secteur | Pas de date publiée. | Bloqué. |
| Objet divisible/indivisible | Ni table ni règle métier. | Bloqué, ne rien inférer. |
| Coûts/seuils décision | Absents. | Bloqué. |
| Dérive/réentraînement | Responsable/fréquence/alertes absents. | Bloqué. |

Les questions exhaustives se trouvent dans `modelisation/docs/questionnaire-modele-enrichi.md`. Toute réponse future doit être ajoutée avec date, source et impact code/données avant de coder.

## Réconciliation avec l'historique

Les documents `03-MODELE/` et certaines structures legacy décrivent encore progression et plafonds par produit. Ils ne sont pas modifiés, mais les décisions terrain de cette page prévalent. Les maps legacy restent seulement pour relire les versions historiques ; elles ne pilotent plus le scoring. Le rapport Claude est préservé dans `2026-09-13-constat-claude-plafonds.md`.
