# Principes UX

## Pour qui nous concevons

Un agent de crédit en agence, qui traite plusieurs dossiers par jour, sur un poste fixe, parfois
avec une connexion instable, souvent avec une formation informatique limitée, et qui a un
sociétaire assis en face de lui pendant qu'il utilise l'outil.

Ce n'est pas un analyste de données devant un tableau de bord. Ce n'est pas un utilisateur qui
explore. C'est quelqu'un qui exécute une tâche répétitive sous le regard d'un tiers.

Trois conséquences qui gouvernent tout le reste :

1. **La densité prime sur l'aération.** Un outil professionnel utilisé vingt fois par jour doit
   montrer beaucoup d'information sans défilement. Le blanc généreux des sites vitrines est ici un
   défaut : il oblige à faire défiler et allonge chaque geste.
2. **Le parcours doit être unique et court.** Pas de multiples façons d'arriver au même écran.
   Un chemin, appris une fois.
3. **L'écran est vu par le sociétaire.** Rien d'humiliant, rien d'illisible, rien qui ressemble à
   un verdict opaque. Le vocabulaire est celui de la coopérative, pas celui du machine learning.

---

## Le parcours principal

C'est le seul parcours qui compte. Il doit être exécutable en moins de deux minutes.

```
Connexion
   │
   ▼
Recherche du sociétaire          ← l'agent tape un nom, rien d'autre
   │
   ▼
Dossier 360°                     ← tout ce que le système sait déjà
   │
   ▼
Saisie de la demande             ← 4 champs, pas davantage
   │
   ▼
Résultat du scoring              ← score, tranche, montant, facteurs
   │
   ▼
Fiche de justification → PDF
```

**Règle de saisie minimale :** l'agent ne saisit **que** ce qui concerne la demande du jour. Tout
ce qui relève du sociétaire est récupéré par le système. Si un champ relatif à l'historique, à
l'épargne ou au groupe apparaît un jour dans un formulaire, c'est une régression fonctionnelle,
pas une amélioration.

---

## Le champ de recherche est le cœur du produit

L'agent tape un nom. C'est tout. À partir de là, le système reconstitue le dossier complet.

Exigences :

- **Recherche incrémentale** : résultats à partir de 2 caractères, latence perçue inférieure à
  200 ms, requête différée de 250 ms après la dernière frappe.
- **Tolérance orthographique** : les noms togolais s'écrivent de plusieurs façons. La recherche
  doit être insensible aux accents, à la casse, et tolérer une approximation (trigrammes
  PostgreSQL). « Kokou Adjo » doit trouver « ADJO Kokou ».
- **Recherche multi-critère implicite** : le même champ accepte un nom, un numéro de membre ou
  un numéro de compte. L'agent ne choisit pas un mode.
- **Résultats désambiguïsants** : nom, numéro de membre, agence, statut. Deux homonymes doivent
  être distinguables sans ouvrir les deux fiches.
- **Entièrement au clavier** : flèches, entrée, échap. Un agent expérimenté ne doit jamais toucher
  la souris sur cet écran.
- **États explicites** : chargement, aucun résultat, trop de résultats, erreur.

---

## Règles d'interaction

| Règle | Détail |
|---|---|
| Une action principale par écran | Un seul bouton plein. Le reste est secondaire ou tertiaire |
| Pas de modale pour une tâche | Les modales servent à confirmer ou à prévisualiser, jamais à saisir un dossier |
| Retour clavier systématique | Entrée valide, Échap ferme, Tab suit l'ordre visuel |
| Aucune action destructrice sans confirmation | Et la confirmation nomme l'objet concerné |
| Le travail n'est jamais perdu | Une saisie en cours survit à un rafraîchissement |
| Pas de défilement horizontal | Jamais, sur aucun écran |

---

## États obligatoires

Tout composant qui affiche des données distantes définit **cinq** états. Un écran livré sans les
cinq n'est pas terminé.

| État | Traitement |
|---|---|
| Chargement | Squelette de la forme finale, jamais un spinner centré sur une page vide |
| Vide | Message expliquant pourquoi c'est vide et ce que l'agent peut faire |
| Erreur | Cause en français, action possible, bouton de reprise |
| Partiel | Les données disponibles sont affichées, l'absence est signalée explicitement |
| Nominal | — |

L'état **partiel** est spécifique à SOLIDA et particulièrement important : quand les variables de
la couche solidaire manquent (segment hors groupe, ou groupe sans historique), on ne masque pas et
on ne bloque pas. On affiche le score du socle en indiquant clairement que la garantie de ce
dossier est l'épargne nantie — c'est **le cas de la majorité du portefeuille**, pas une exception à
justifier.

---

## Restitution du score : règles impératives

Le moment où le score s'affiche est le moment le plus délicat du produit, parce que le sociétaire
regarde l'écran.

| Règle | Raison |
|---|---|
| Le score est un entier, jamais un pourcentage de risque | Sur données synthétiques, une probabilité affichée est indéfendable |
| Toujours accompagné de sa tranche en toutes lettres | Un nombre seul ne veut rien dire pour l'agent |
| Toujours accompagné des facteurs déterminants | Une décision sans justification est contraire au principe du produit |
| Jamais de rouge agressif sur un refus | Le sociétaire est en face. Rouge sobre, pas alarmant |
| Jamais d'animation spectaculaire | Une jauge qui se remplit dramatiquement ridiculise la situation |
| Le mot « recommandation » figure toujours | La décision reste humaine, l'interface doit le dire |
| Le vocabulaire ML n'apparaît jamais | Pas de « probabilité », « modèle », « feature », « prédiction » à l'écran |

---

## Performance perçue

| Cible | Valeur |
|---|---|
| Suggestions de recherche | < 200 ms |
| Ouverture du dossier | < 500 ms |
| Calcul du score | < 1 s |
| Génération du PDF | < 3 s, avec indication de progression |

Au-delà de 300 ms, afficher un squelette. Au-delà de 2 s, afficher une progression nommée
(« Génération de la fiche… »), pas un spinner anonyme.
