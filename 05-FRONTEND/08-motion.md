# Motion — spécification des animations

## Philosophie

Le mouvement **confirme une action** ou **explique une transition spatiale**. Il ne décore jamais.
C'est ce qui sépare une interface premium d'une interface qui « fait IA » : une animation planardie,
spécifiée à la milliseconde, appliquée au bon endroit, plutôt qu'un « effet cool » générique.

Règle fondatrice : **une animation doit avoir une raison.** Si on ne peut pas dire ce qu'elle
confirme ou explique, on la retire.

## Librairie

**Motion** (motion.dev, anciennement Framer Motion), pour les animations d'état d'interface. C'est
la même librairie que celle citée comme « Framer Motion » dans `03-usage-des-librairies.md` ; le nom
a changé, l'usage reste restreint.

Pas de librairie d'animation au défilement (type GSAP ScrollTrigger) : elle sert les pages
marketing, pas un outil de guichet. On n'a pas de page marketing dans le produit.

## Les six animations autorisées — liste fermée

Aucune autre animation n'est ajoutée sans passer par l'équipe.

| # | Animation | Déclencheur | Durée | Courbe | Ce qu'elle explique |
|---|---|---|---|---|---|
| 1 | Apparition d'un panneau (Sheet, Dialog) | Ouverture | 180 ms | `ease-out` | D'où vient l'élément |
| 2 | Bascule d'onglet | Clic | 150 ms | `ease-out` | La continuité entre deux vues |
| 3 | Apparition des lignes de contribution | Affichage du score | 200 ms, décalage 25 ms/ligne | `ease-out` | La lecture séquentielle des facteurs |
| 4 | Compteur du score | Affichage du résultat | 600 ms | `ease-out` | Le poids du moment de décision |
| 5 | Réorganisation de liste | Tri, filtre | 200 ms | `layout` | Ce qui a bougé et où |
| 6 | Transition d'état de bouton | Survol, pression | 120 ms | `ease-out` | La réactivité, **par la couleur, pas par l'ombre** |

## Détail des deux animations signatures

### Le compteur de score (#4)

Le score monte de 0 à sa valeur en 600 ms, une seule fois, sans rebond, sans dépassement, sans
accélération théâtrale. C'est le seul moment « spectaculaire » toléré de l'application, et il reste
sobre.

- Police IBM Plex Mono, chiffres tabulaires (le nombre ne « saute » pas en largeur pendant qu'il
  monte).
- La barre de position sous le score se remplit **en même temps**, synchronisée.
- **Jamais** de dégradé, de lueur, ou de changement de couleur pendant la montée.
- Composant : `NumberTicker` de Magic UI, ou une animation Motion simple. Rien d'autre de Magic UI.

### Les lignes de contribution (#3)

Les facteurs apparaissent l'un après l'autre, de haut en bas, décalés de 25 ms. L'effet dure moins
d'une demi-seconde au total et donne le sentiment que le système « déroule » son raisonnement. Il ne
se rejoue pas si l'utilisateur revient sur l'écran dans la même session.

## Ce qui est strictement interdit

| Interdit | Raison |
|---|---|
| Animation au défilement, parallaxe | Registre marketing, ralentit un outil de guichet |
| Effet d'entrée sur chaque carte au chargement | Signature « IA », coûte du temps à chaque écran |
| Rebond, ressort, dépassement | Registre ludique, inadapté à une décision de crédit |
| Animation en boucle | Distrait, consomme |
| Ombre animée sur un bouton | On ne met pas d'ombre sur les boutons du tout |
| Durée > 300 ms hors compteur de score | Un outil professionnel doit répondre vite |
| Transition de page élaborée | Le changement d'écran est instantané ou presque |
| Skeleton qui pulse de façon trop marquée | Un frémissement discret suffit |

## Accessibilité du mouvement — non négociable

`prefers-reduced-motion` est **respecté partout**. Si l'utilisateur l'a activé au niveau système :

| Animation | Comportement dégradé |
|---|---|
| Compteur de score | Le score s'affiche directement à sa valeur finale |
| Lignes de contribution | Apparaissent toutes en même temps, sans décalage |
| Panneaux, onglets | Changement instantané |
| Boutons | Changement de couleur immédiat |

Aucune information ni aucune fonction ne dépend d'une animation. Une animation supprimée ne doit
jamais rendre l'interface moins compréhensible.

## Performance

| Règle | Motif |
|---|---|
| Animer uniquement `transform` et `opacity` | Ce sont les seules propriétés animables sans recalcul de mise en page |
| Jamais animer `width`, `height`, `top`, `left` | Provoque des reflows, saccade |
| Pas plus d'une animation signature par écran | Deux moments spectaculaires simultanés = zéro |
| 60 images par seconde ou on retire | Une animation qui saccade est pire que pas d'animation |

## Résumé pour l'agent qui code

Si tu hésites à ajouter une animation : ne l'ajoute pas. Les six ci-dessus suffisent à donner une
sensation premium. Le premium vient de la **retenue** et de la précision des six, pas de leur nombre.
