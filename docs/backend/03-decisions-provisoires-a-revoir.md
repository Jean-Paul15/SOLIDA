# Décisions provisoires à revoir

Ce fichier est la référence unique pour tout ce qui, dans le backend, a été fixé arbitrairement
faute du vrai modèle entraîné ou d'un arbitrage métier définitif. Rien de ce qui suit n'est une
vérité figée : c'est un point de départ pour que la chaîne fonctionne dès maintenant.

## Le modèle lui-même

`ModeleConstant` renvoie une probabilité de défaut fixe (0,09 — le taux de créances en souffrance
cible du générateur, pas une valeur inventée). **À remplacer entièrement** une fois le modèle réel
entraîné et calibré : c'est le seul changement attendu, aucun code au-dessus (scorecard, grille,
cascade, plafond progressif, persistance, HTTP) ne devrait avoir à changer, puisque tout dépend du
modèle uniquement via le port `ModeleScoring`.

## Paramètres de la scorecard (mise à l'échelle probabilité → score)

PDO = 20, score de référence = 600, rapport de référence = 50. Valeurs de travail cohérentes entre
elles, pas calibrées sur un vrai modèle. À recalibrer une fois la vraie distribution de probabilité
connue (un modèle mal calibré rend cette mise à l'échelle trompeuse).

## Paramètres de la grille de décision

`marge` (0,15) et `lgd` — perte en cas de défaut — (0,75), plus les multiplicateurs de zone (0,6 /
1 / 1,6). Ce ne sont pas des choix techniques : ils traduisent un arbitrage risque/approbation qui
appartient à la coopérative, pas à qui écrit le code. Les valeurs actuelles reprennent le prototype
`simulateur/decision.py` pour construire et tester le mécanisme — pas la vérité finale. Réglage
prévu par le superviseur (écran de paramétrage de la grille), affiné par le calibrage du modèle
réel une fois qu'il existe.

## Paramètres du crédit progressif

`coefficient_progression` (1,5), `montant_plancher` (50 000 FCFA), `plafond_produit`
(3 000 000 FCFA — le plafond que le système ne dépasse jamais, quel que soit le calcul),
`plafond_primo_emprunteur` (150 000 FCFA), et les constantes de modulation par le risque (1,3 / 2,0
/ 0,4 / 1,2). Même statut que la grille : point de départ ajustable par la coopérative, pas figé.

## Approximations de l'adaptateur CORE-SIM

Le générateur produit des données brutes mais pas d'échéancier de remboursement détaillé ni
certains champs de présentation. Ces valeurs sont **estimées, pas mesurées** :

- `capital_restant_du` : amortissement linéaire pour un crédit en cours ; montant intégral pour un
  crédit en souffrance (aucune donnée de remboursement partiel n'existe) ; zéro pour un crédit
  soldé.
- `statut` du sociétaire (actif/inactif/radié) : toujours "actif", le générateur ne modélise aucun
  churn.
- `nom_groupe` et `statut` du groupe : dérivés (nom depuis l'identifiant, statut depuis le taux de
  remboursement), le générateur ne produit ni l'un ni l'autre directement.
- `secteur` d'activité affiché au guichet : déduit du segment (agricole → agriculture, etc.), le
  générateur ne modélise pas de secteur d'activité distinct du segment.

## Simplifications d'architecture pour cette passe

- **Pas de feature store historisé, pas de batch.** Les features sont calculées à la demande à
  partir de CORE-SIM à chaque requête. Correct fonctionnellement, mais ne reflète pas encore la
  fraîcheur/staleness que la cascade est censée surveiller dans une vraie exploitation continue.
- **Recherche et dossier lisent CORE-SIM directement**, pas un index dédié pré-calculé. Suffisant
  au volume d'un hackathon, à revoir si la volumétrie ou la latence l'exigent.
- **Authentification : une seule session révocable de 8 heures** (stratégie base de données), pas
  un JWT court de 15 minutes séparé d'un renouvellement long. Choix délibéré pour la simplicité
  (moins de composants, plus facile à auditer) : la propriété qui compte — révocation côté serveur
  — est déjà pleinement assurée par ce choix unique.
- **Fiche de justification : pas de génération PDF.** L'écran restitue le contenu en JSON/HTML ; la
  génération PDF (rendu serveur, archivage) reste à construire.
