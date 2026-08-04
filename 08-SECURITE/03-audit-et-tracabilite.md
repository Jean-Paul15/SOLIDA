# Audit et traçabilité

## Pourquoi c'est structurant

Dans une institution financière, une décision non traçable n'existe pas. Trois raisons :

1. **Contrôle interne** : l'inspection doit pouvoir vérifier les décisions.
2. **Contestation** : un sociétaire doit pouvoir faire réexaminer son dossier.
3. **Amélioration** : le recalibrage sur données réelles suppose de savoir ce qui a été décidé et
   ce qui s'est ensuite passé.

## Ce qui est tracé

### À chaque scoring
Entrées saisies, features utilisées **avec leurs valeurs**, versions du modèle et de la grille,
probabilité, score, tranche, montant recommandé, mode de calcul, décomposition complète,
avertissements, agent, horodatage.

**Le point critique est de conserver les valeurs des features, pas seulement leurs identifiants.**
Sans cela, le rejeu est impossible dès que le feature store est rafraîchi.

### À chaque décision finale
Décision de l'agent, montant accordé, motif d'écart si écart, horodatage.

### À chaque action sensible
Connexion, échec de connexion, consultation de dossier, génération de fiche, modification de
grille, promotion de modèle, création ou modification d'utilisateur.

## Propriétés du journal

| Propriété | Mise en œuvre |
|---|---|
| Insertion seule | Aucun `UPDATE` ni `DELETE` ; droits restreints en base |
| Horodaté | `TIMESTAMPTZ`, horloge serveur |
| Attribué | Toujours un acteur identifié, jamais « système » sans précision |
| Complet | Une action sensible sans trace est un défaut bloquant |
| Consultable | Écran E7, filtrable |
| Exportable | CSV pour l'inspection |

## Rejeu d'une décision

Fonction essentielle. Étant donné un `decision_id`, on recharge les entrées et les features
persistées, le modèle et la grille d'époque, on recalcule, et on vérifie que le résultat est
identique.

**Un test automatique rejoue un échantillon de décisions à chaque exécution de la CI.** Si le
rejeu diverge, c'est qu'une modification a cassé la reproductibilité — probablement un changement
de code non versionné dans le calcul.

## Indicateur clé : le taux d'écart

Part des décisions où l'agent s'écarte de la recommandation.

| Interprétation | Signification |
|---|---|
| Très faible (< 5 %) | L'agent suit aveuglément. Contraire à l'esprit « décision humaine » |
| Modéré (10 – 25 %) | Sain. L'outil éclaire sans se substituer |
| Élevé (> 40 %) | Le modèle est mal calibré, ou la grille est mal réglée, ou l'outil n'est pas accepté |

Analysé par agent, par agence et par tranche. C'est l'indicateur de pilotage le plus riche du
système, et un excellent sujet à présenter au jury : il montre qu'on a pensé l'adoption, pas
seulement l'algorithme.

## Périmètre hackathon

P1 : persistance de `decision_scoring` avec décomposition complète — **cela doit être fait dès le
premier scoring rendu**, sinon les décisions du jour 2 ne seront pas rejouables.
P2 : écran de registre, export, fonction de rejeu.
