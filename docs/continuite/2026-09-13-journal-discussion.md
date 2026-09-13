# Journal de discussion conservé pour reprise

Ce journal est une synthèse fidèle, sans secret ni document local, des réponses utilisateur qui orientent le travail. Il complète la transmission complète ; il ne remplace pas les sources techniques.

## Générateur J1-05 à J1-13

- Les issues du crédit ne sont pas des variables d'octroi.
- Aucun montant par produit n'est fixé ; 100 M FCFA est le maximum institutionnel.
- Aucun coefficient de progression n'est appliqué après remboursement correct ; montant et faisabilité sont choisis avec le client.
- Toutes les périodicités annoncées sont possibles, sans périodicité produit imposée.
- Historique client conservé dès création de compte.
- Crédit groupe : remboursement et retards groupe seulement.
- Nantissement : taux jusqu'à 10 % annoncé, mais intérêts d'épargne non générés faute de fréquence/règle.
- Solde libre : dépôts, retraits, transferts et restitutions chronologiques.
- Âge disponible mais sans règle de risque ni refus automatique à 73 ans.

## SOCLE EBM J1-14 à J1-21

- Objectif : environ 10 000 lignes ; résultat exact 9 818 crédits entraînables.
- `date_deblocage` accepté comme proxy de la demande, indispensable à l'anti-fuite.
- Revenu et charge mensualisée sont utiles : revenu est feature, ratio endettement est feature, charge brute du nouveau crédit ne l'est pas.
- GIE, garanties, produit, taux, périodicité, statut, défaut et retards du crédit courant sont exclus du SOCLE pour raison temporelle ou de gouvernance.
- EBM doit exploiter nativement les types pandas, catégories et valeurs manquantes. Pas de dummy, standardisation ou imputation dans le dataset EBM.
- Les seuils de sélection et de décision doivent être choisis après les métriques, pas pendant l'entraînement.
- Objet divisible/indivisible : aucune donnée/règle, donc aucune inférence.

## Suite demandée

La prochaine session doit préparer couche solidaire, modèle enrichi et moteur de décision en s'appuyant sur les tables datées. Elle doit commencer par le questionnaire enrichi et marquer toute réponse inconnue comme décision manquante. Les réponses déjà connues et les blocages sont dans `2026-09-13-transmission-complete.md`.

## Provenance

- Décisions métier : messages utilisateur de cette discussion, septembre 2026.
- Constat de plafonds : rapport transmis par Claude dans cette discussion, conservé dans le fichier voisin.
- Code, tests et métriques : artefacts versionnés et DVC de ce dépôt.
