# Usage des librairies front

## Stack retenue

| Librairie | Rôle | Discipline d'usage |
|---|---|---|
| **Next.js 15** | Framework, App Router, Server Components | Structurant |
| **Tailwind CSS 4** | Style utilitaire, jetons via `@theme` | Structurant |
| **shadcn/ui** | Primitives d'interface accessibles | **Base de tous les composants** |
| **Lucide React** | Icônes | Usage large, avec sélection stricte |
| **Recharts** | Graphiques | Usage ciblé |
| **Framer Motion** | Animation | **Usage restreint** |
| **Magic UI** | Composants animés | **Usage très restreint** |
| **Aceternity UI** | Composants spectaculaires | **Quasiment interdit dans l'application** |

Le tableau ci-dessus se lit de haut en bas comme une échelle de méfiance croissante. Les trois
dernières lignes sont celles qui peuvent faire basculer l'interface dans le registre « démonstration
générée » que nous refusons.

---

## shadcn/ui — la fondation

Tous les composants d'interface partent de shadcn/ui. Aucun composant interactif n'est écrit
à la main s'il existe en équivalent shadcn.

**Composants utilisés dans SOLIDA :**

`Button`, `Input`, `Label`, `Select`, `Command` (indispensable pour la recherche),
`Popover`, `Dialog`, `Table`, `Badge`, `Card`, `Separator`, `Tabs`, `Tooltip`,
`Skeleton`, `Alert`, `Sonner` (notifications), `Form`, `ScrollArea`, `Avatar`.

**Adaptation obligatoire :** les valeurs par défaut de shadcn sont plus aérées et plus arrondies
que notre design system. Chaque composant importé est ajusté une seule fois, au moment de son
ajout, pour respecter les jetons de `02-design-system.md` : hauteur 36 px, rayon 6 px, ombre
supprimée sur les surfaces non flottantes. On ajuste le composant à la source, jamais écran par
écran avec des classes de correction.

**Le composant `Command` est central.** C'est lui qui porte la recherche de sociétaire :
combobox filtrable, navigable au clavier, accessible. Ne pas réimplémenter.

---

## Lucide React — icônes

**Règles :**

- Taille unique dans l'application : 16 px. Exception : 20 px dans l'en-tête.
- Épaisseur de trait : 1,75.
- Une icône n'est jamais seule si elle porte une action non évidente : elle est accompagnée d'un
  libellé ou d'une infobulle.
- **Icônes proscrites** : `Sparkles`, `Wand2`, `Bot`, `Brain`, `Zap`, `Rocket`, et tout ce qui
  évoque la magie ou l'intelligence artificielle. Elles suggèrent que la décision est produite par
  une boîte noire, ce qui est exactement le message inverse du produit.
- **Icônes du domaine** : `Search`, `User`, `Users`, `Wallet`, `TrendingUp`, `TrendingDown`,
  `FileText`, `Download`, `Network`, `ShieldCheck`, `AlertTriangle`, `Clock`, `Building2`,
  `CircleCheck`, `CircleAlert`, `CircleX`.

---

## Recharts — graphiques

**Où l'utiliser :**

| Écran | Graphique | Justification |
|---|---|---|
| Dossier 360° | Courbe d'évolution du solde d'épargne sur 12 mois | Montre la régularité, signal métier fort |
| Dossier 360° | Barres de régularité des dépôts par mois | Lisible immédiatement |
| Résultat de scoring | Barres horizontales divergentes des contributions en points | C'est la scorecard, cœur de l'explicabilité |
| Supervision modèle (P2) | Courbe ROC, courbe de calibration | Public technique uniquement |

**Où ne pas l'utiliser :** nulle part ailleurs. Pas de camembert, pas de jauge circulaire animée,
pas de graphique décoratif. Un graphique qui n'aide pas à décider est du bruit.

**Style imposé :**
- Pas de grille verticale, grille horizontale en `--neutre-200` à 1 px.
- Pas de légende si une seule série.
- Pas d'animation à l'entrée, ou 200 ms maximum.
- Couleurs issues des jetons, jamais la palette par défaut de Recharts.
- Infobulle personnalisée, jamais celle par défaut.

---

## Framer Motion — usage restreint

**Principe :** l'animation confirme une action de l'utilisateur ou explique une transition
spatiale. Elle ne décore jamais.

**Usages autorisés, liste fermée :**

| Cas | Durée | Courbe |
|---|---|---|
| Apparition d'un panneau ou d'une modale | 180 ms | `ease-out` |
| Bascule entre onglets | 150 ms | `ease-out` |
| Apparition des lignes de contribution du score | 200 ms, décalage 25 ms | `ease-out` |
| Compteur du score qui monte à l'affichage | 600 ms | `ease-out` |
| Réorganisation de liste | 200 ms | `layout` |

**Interdits :** animation au défilement, parallaxe, effets d'entrée sur chaque carte au chargement,
rebond, animation en boucle, durée supérieure à 300 ms hors compteur de score.

**Règle transversale :** respecter `prefers-reduced-motion`. Si l'utilisateur l'a activé, toutes
les animations sont désactivées, y compris le compteur de score.

---

## Magic UI — usage très restreint

Magic UI contient d'excellents composants et beaucoup d'effets qui ruineraient la crédibilité de
l'outil. **Deux usages autorisés, aucun autre :**

1. **`NumberTicker`** sur l'affichage du score, et uniquement là. Le score qui s'incrémente jusqu'à
   sa valeur donne du poids au moment de la décision sans être spectaculaire.
2. **`AnimatedBeam`** sur l'écran de connexion ou une page de présentation, pour évoquer le flux
   d'épargne. Jamais dans l'application elle-même.

**Explicitement interdits :** `BorderBeam`, `ShimmerButton`, `Meteors`, `Particles`, `RetroGrid`,
`NeonGradientCard`, `Confetti`, et tout composant à effet lumineux ou particulaire.

---

## Aceternity UI — quasiment interdit

Aceternity est conçu pour des pages de présentation marketing. Dans une application de décision de
crédit, ses composants sont hors registre.

**Seul usage envisageable :** une page publique de présentation du projet, hors du produit, si
l'équipe décide d'en faire une pour la démonstration. Dans ce cas, un seul effet, choisi, et pas
trois.

**Dans l'application : aucun composant Aceternity.** Si un développeur en importe un, c'est un
motif de retour en revue.

---

## Le groupe de caution est un tableau, pas un graphe

Aucune bibliothèque de visualisation de graphe (`react-force-graph`, `d3-force`) n'entre dans le
projet. L'écran E5 (voir `04-ecrans-specifications.md`) affiche le groupe de caution comme une
**liste triable**, avec le composant `Table` de shadcn déjà utilisé pour l'historique de crédit sur
E2. Décision cohérente avec ADR-016 (`01-ARCHITECTURE/07-strategie-graphe.md`) : la structure réelle
d'un groupe de 4 à 15 membres n'a rien à gagner à un rendu en nœuds et arêtes, et un tableau
s'exporte nativement dans la fiche PDF sans code de rendu supplémentaire.

---

## Règle de dernier recours

Avant d'ajouter une librairie non listée ici : elle n'est pas autorisée. Voir `AGENTS.md`,
règle zéro. La demande passe par l'équipe et par une entrée dans le journal de décisions.
