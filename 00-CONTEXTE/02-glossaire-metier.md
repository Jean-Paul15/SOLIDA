# Glossaire métier

Ce vocabulaire est **normatif**. Il est utilisé tel quel dans le code, les interfaces, les schémas
de base et la documentation. Ne pas introduire de synonyme.

## Acteurs

| Terme | Définition | Ne pas dire |
|---|---|---|
| **Sociétaire** | Personne membre de la coopérative, détentrice de parts sociales | « client », « utilisateur » |
| **Agent de crédit** | Employé qui instruit les dossiers et rencontre les sociétaires | « conseiller », « opérateur » |
| **Comité de crédit** | Instance qui arbitre les dossiers au-dessus d'un seuil | « validateur » |
| **Superviseur** | Responsable d'agence, paramètre la grille de décision | « manager » |
| **Auditeur** | Consulte le registre des décisions, ne décide pas | « contrôleur » |

## Institutions

| Terme | Définition |
|---|---|
| **IMF** | Institution de microfinance |
| **SFD** | Système financier décentralisé — terme réglementaire BCEAO pour les IMF de l'UEMOA |
| **Coopérative financière** | Forme juridique visée par la CIF : mutuelle ou coopérative d'épargne et de crédit |
| **CIF** | Confédération des Institutions Financières d'Afrique de l'Ouest |
| **Faîtière** | Fédération nationale de coopératives d'épargne et de crédit, membre de la CIF |
| **FUCEC-TOGO** | Faîtière des Unités Coopératives d'Épargne et de Crédit du Togo, membre CIF |
| **SIG (CIF)** | Système Unique d'Information de la CIF, reliant les six faîtières depuis 2020 |
| **BCEAO** | Banque Centrale des États de l'Afrique de l'Ouest |
| **APSFD** | Association Professionnelle des SFD (déclinaison nationale) |

## Crédit

| Terme | Définition |
|---|---|
| **Demande de crédit** | Sollicitation instruite, qu'elle aboutisse ou non. Objet d'entrée du scoring |
| **Crédit** | Demande accordée et débloquée |
| **Cycle** | Rang du crédit pour un sociétaire donné (1er, 2e…). Base du crédit progressif |
| **Crédit progressif** | Pratique consistant à augmenter le plafond à chaque cycle remboursé sans incident |
| **Échéance** | Ligne de l'échéancier : capital + intérêt dus à une date |
| **Créance en souffrance** | Créance dont le retard dépasse le seuil réglementaire (à confirmer : 90 jours) |
| **PAR30 / PAR90** | Portfolio at Risk : encours dont au moins une échéance a plus de 30 / 90 jours de retard |
| **Taux de dégradation du portefeuille** | Part de l'encours en souffrance. Norme BCEAO : 3 % |
| **TAEG** | Taux annuel effectif global. Plafonné à 24 % pour les SFD de l'UEMOA |

## Garantie et couche solidaire

| Terme | Définition |
|---|---|
| **Segment** | Catégorie de produit du sociétaire : salarié, individuel, jeune, femme_gie, agricole. Détermine le traitement du risque |
| **Groupement (GIE)** | Groupement d'intérêt économique, typiquement de femmes — le segment où s'active la couche solidaire |
| **Groupe de caution solidaire** | Groupe de 4 à 15 sociétaires du segment groupement, se portant mutuellement garants |
| **Caution solidaire** | Mécanisme remplaçant la garantie matérielle par la solidarité du groupe, propre au segment groupement |
| **Couche solidaire** | Bloc d'agrégats (taux de remboursement du groupe, taille, « déjà secouru ») calculé en SQL classique sur le seul segment groupement — jamais une structure de graphe (ADR-016) |
| **Garant** | Sociétaire qui s'engage pour un autre |
| **Bénéficiaire** | Sociétaire pour lequel un garant s'engage |
| **Garantie appelée** | Garantie mise en jeu, le garant ayant payé à la place du débiteur |
| **Déjà secouru** | Le sociétaire a déjà bénéficié d'un paiement par son garant — signal individuel fort de la couche solidaire |
| **Épargne nantie** | Épargne bloquée en garantie du crédit — garantie de droit commun, majoritaire dans le modèle mutualiste |
| **Tontine** | Épargne rotative informelle. Hors périmètre SOLIDA sauf si encadrée par l'IMF |

## Scoring

| Terme | Définition |
|---|---|
| **Trajectoire d'épargne** | Lecture dynamique de l'épargne (régularité, tendance, effort, ancienneté de la relation), signal central du socle — pas un simple solde |
| **Probabilité de défaut (PD)** | Sortie brute du modèle, entre 0 et 1 |
| **Score** | Entier obtenu par transformation affine des log-odds. Score élevé = risque faible |
| **PDO** | *Points to Double the Odds* — points qui doublent le rapport bons / mauvais |
| **Scorecard** | Grille de points par variable |
| **Grille de décision** | Correspondance tranche de score → décision recommandée + plafond, seuils dérivés de la matrice de coûts |
| **Cascade** | Architecture à deux niveaux : socle individuel (épargne, remboursement), puis couche solidaire conditionnelle sur le segment groupement |
| **Plafond conseillé** | Montant recommandé, sortie du moteur de crédit progressif (historique remboursé × coefficient, modulé par le risque) |
| **Trajectoire de progression** | Plafonds accessibles sur les cycles suivants si le sociétaire rembourse sans incident |
| **Conditions de réexamen** | Leviers concrets et vérifiables dans le système qu'un sociétaire peut activer pour faire réexaminer sa demande |
| **Démarrage à froid** | Situation d'un sociétaire sans historique personnel ni groupe historisé |
| **Fiche de justification** | Document restituant les facteurs déterminants d'une décision et, le cas échéant, les conditions de réexamen |
| **Calibration** | Vérification que la probabilité prédite correspond à la fréquence observée |
| **Dérive** | Écart entre la distribution d'entraînement et la distribution observée en production |

## Systèmes

| Terme | Définition |
|---|---|
| **CORE-SIM** | Base simulant le système de gestion de la coopérative. Lecture seule |
| **SOLIDA** | Notre système : trajectoire d'épargne, couche solidaire, modèles, scores, décisions, audit |
| **Contrat d'intégration** | Ensemble minimal de champs qu'une IMF doit exposer pour brancher SOLIDA |
| **Feature store** | Table de variables pré-calculées par sociétaire, rafraîchie en batch |
