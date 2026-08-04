# Design system

Ce fichier est **normatif**. Aucune valeur de couleur, d'espacement ou de rayon n'est écrite
ailleurs dans le code. Tout passe par les jetons définis ici.

---

## 1. Ce que nous refusons explicitement

Ces interdits existent parce que l'interface doit ressembler à un outil bancaire conçu par des
professionnels, et non à une démonstration générée automatiquement. Le jury verra plusieurs
interfaces dans la journée ; celles qui se ressemblent toutes se remarquent.

| Interdit | Pourquoi |
|---|---|
| Dégradés violet → bleu, cyan → magenta | Signature visuelle immédiatement reconnaissable des interfaces générées |
| Glassmorphism, flou d'arrière-plan | Nuit à la lisibilité, mode passager, sans rapport avec un outil métier |
| Bordures lumineuses, halos, effets de brillance | Aucun outil financier sérieux n'en comporte |
| Ombres portées marquées sur cartes et boutons | Voir la règle d'élévation ci-dessous |
| `rounded-2xl` / `rounded-3xl` généralisés | Aspect « application grand public » inadapté |
| Emoji dans l'interface | Registre inapproprié pour une décision de crédit |
| Icônes d'étincelles, de baguette magique, de robot | Suggère que la décision est magique. Contraire au produit |
| Mode sombre par défaut | Les agences sont éclairées. Le sombre nuit à la lecture de tableaux denses |
| Animations d'entrée sur chaque élément | Ralentit un outil utilisé vingt fois par jour |
| Polices par défaut non choisies | Trahit l'absence de décision typographique |
| Cartes surdimensionnées avec beaucoup de blanc | Densité insuffisante pour un poste de travail |
| **Cartes imbriquées** (carte dans une carte dans une carte) | Marqueur « IA » classique : l'imbrication remplace la hiérarchie réelle. Deux niveaux de conteneur maximum |
| **Texte en dégradé** sur un chiffre ou un titre | Signature générée. Un score, un montant, un titre sont d'une seule couleur pleine |
| Layout « gros chiffre + petit label + trait dégradé à gauche » répété partout | Ce motif exact est dans la quasi-totalité des tableaux de bord générés. Notre écran de score s'en distingue par la décomposition, le monospace et l'absence de dégradé |
| Police Inter, Roboto, Arial, Space Grotesk | Polices par défaut des interfaces générées. On utilise IBM Plex, choisi explicitement |
| Accents cyan, halos, « sparkle pour faire ressortir » | Registre « magique », contraire à un outil de décision |

**Pourquoi cette liste est aussi précise :** un outil génératif retombe toujours sur la même
moyenne (police par défaut, dégradé violet-bleu, cartes arrondies empilées) faute de contraintes.
La façon d'en sortir n'est pas seulement de dire ce qu'on veut, mais d'**interdire explicitement**
ces défauts. C'est la raison d'être de ce tableau. Un écran qui, tel quel, pourrait aussi bien être
celui d'un CRM ou d'un outil de gestion de projet a échoué : il ne dit rien de SOLIDA.

---

## 2. Couleurs

La palette dérive du logo SOLIDA : fond pétrole, nœuds or et blancs.

### Marque

```
--solida-teal-900 : #0B3040    Fonds sombres, en-tête d'application
--solida-teal-800 : #0F4457    Couleur primaire (actions, liens actifs)
--solida-teal-700 : #14607A    Survol du primaire
--solida-teal-600 : #1A7B93    Accents froids, sélection
--solida-teal-100 : #DCEBF0    Fonds de sélection très clairs
--solida-teal-50  : #F0F6F8    Fonds de section

--solida-gold-600 : #C9821F    Or foncé, texte sur fond clair
--solida-gold-500 : #F5A43B    Or de marque, accent
--solida-gold-100 : #FDF0DC    Fond d'accent discret
```

**Règle d'usage de l'or :** l'or est un **accent**, jamais une surface. Il souligne, il marque un
état actif, il attire l'œil sur un point unique par écran. Un bouton principal en or plein est une
faute. Surface maximale d'or sur un écran : environ 5 %.

### Neutres

Échelle chaude et sobre, non bleutée.

```
--neutre-950 : #1A1A18    Texte principal
--neutre-700 : #4A4A46    Texte secondaire
--neutre-500 : #7A7A74    Texte tertiaire, libellés
--neutre-300 : #C9C9C3    Bordures marquées
--neutre-200 : #E2E2DD    Bordures standard
--neutre-100 : #F2F2EE    Fonds de zone
--neutre-50  : #F9F9F7    Fond d'application
--blanc      : #FFFFFF    Surfaces
```

### Sémantique de décision

Volontairement désaturées. Le sociétaire regarde l'écran.

```
--decision-accord       : #1F7A5C    fond #E8F2EE
--decision-conditionnel : #A97814    fond #FAF1DE
--decision-comite       : #B85C24    fond #FBEDE3
--decision-refus        : #A63A31    fond #F7E9E7
```

**Aucun rouge vif.** `#A63A31` est un rouge brique, lisible et grave, non alarmant.

### Sémantique système

```
--info    : #14607A
--succes  : #1F7A5C
--alerte  : #A97814
--erreur  : #A63A31
```

---

## 3. Typographie

### Familles

| Usage | Police | Graisses |
|---|---|---|
| Interface | **IBM Plex Sans** | 400, 500, 600 |
| Chiffres, scores, identifiants, montants | **IBM Plex Mono** | 400, 500 |

**Pourquoi IBM Plex Sans :** couverture complète du français accentué, chiffres tabulaires natifs,
registre institutionnel et technique adapté à un outil financier, licence libre, et surtout : ce
n'est pas la police par défaut que tout le monde utilise.

**Variante autorisée** (à activer par un seul jeton, pas à improviser) : `Source Serif 4` en 600
pour les titres d'écran uniquement. Une serif sur les titres est un marqueur fort d'interface
conçue, pas générée. Si elle est activée, elle ne sert **qu'aux titres d'écran**, jamais au corps.

### Échelle

| Jeton | Taille / interligne | Usage |
|---|---|---|
| `texte-xs` | 11 / 16 | Libellés de tableau, mentions |
| `texte-sm` | 14 / 20 | Corps par défaut de l'interface |
| `texte-base` | 16 / 24 | Corps de lecture, descriptions |
| `texte-lg` | 18 / 26 | Titres de section |
| `texte-xl` | 22 / 30 | Titre d'écran |
| `texte-score` | 56 / 60 | Affichage du score, IBM Plex Mono 500 |

L'échelle est volontairement resserrée. Un outil dense n'a pas besoin de sept niveaux de titre.

**`texte-sm` et `texte-base` révisés à la hausse** (initialement 13/15) après test réel de l'écran
de connexion à 100 % de zoom sur écran standard : trop petit à la lecture. La densité reste
gouvernée par l'espacement (section 4), pas par une taille de texte illisible.

**Échelle globale à 110 %** : après comparaison de plusieurs niveaux de zoom navigateur par un
testeur réel, le rendu à 110 % a été jugé plus confortable que 100 %. Plutôt que de dépendre d'un
réglage de zoom, `html { font-size: 110%; }` reproduit cet effet par défaut, et les jetons `texte-*`
sont exprimés en `rem` (pas en `px`) pour suivre ce changement. Les composants shadcn (hauteurs,
espacements internes) suivent automatiquement puisqu'ils sont eux-mêmes en `rem`.

### Règles numériques

Tous les chiffres alignables utilisent `font-variant-numeric: tabular-nums`. Sans cela, une colonne
de montants ne s'aligne pas et l'ensemble paraît amateur.

**Format des montants :** `1 250 000 FCFA` — espace fine insécable comme séparateur de milliers,
devise après le nombre, jamais de décimales. Le formatage est centralisé dans une fonction unique
du domaine front, jamais réécrit localement.

---

## 4. Espacement

Base de 4 px. Valeurs autorisées : 4, 8, 12, 16, 20, 24, 32, 40, 48. Rien d'autre.

### Densité imposée

| Élément | Hauteur |
|---|---|
| Ligne de tableau | 40 px |
| Champ de saisie | 36 px |
| Bouton standard | 36 px |
| Bouton compact | 30 px |
| Barre d'en-tête | 56 px |
| Padding interne de carte | 16 px |

Ces valeurs sont plus serrées que les valeurs par défaut de la plupart des bibliothèques.
C'est délibéré.

---

## 5. Rayons

| Jeton | Valeur | Usage |
|---|---|---|
| `rayon-sm` | 4 px | Badges, puces |
| `rayon-md` | 6 px | **Par défaut** : boutons, champs, menus |
| `rayon-lg` | 8 px | Cartes, panneaux |
| `rayon-full` | 9999 px | Uniquement avatars et pastilles de statut |

Aucune valeur au-dessus de 8 px sur un conteneur.

---

## 6. Élévation — règle stricte

**Trois niveaux, pas quatre.**

| Niveau | Effet | Usage |
|---|---|---|
| 0 | Aucune ombre, bordure `1px solid --neutre-200` | **Cartes, panneaux, tableaux, boutons.** Cas par défaut, largement majoritaire |
| 1 | `0 2px 6px rgba(26,26,24,0.07)` + bordure | Éléments flottants : menu déroulant, popover, infobulle, liste de suggestions |
| 2 | `0 8px 24px rgba(26,26,24,0.12)` + bordure | Boîtes de dialogue et notifications uniquement |

**Un bouton n'a jamais d'ombre.** Un bouton au repos, au survol ou pressé se distingue par la
couleur de fond et la bordure, pas par une élévation. C'est la demande explicite du produit et
c'est aussi ce que font les interfaces bancaires sérieuses.

La séparation visuelle se fait par **bordure et par fond**, pas par ombre. Une page composée de
cartes qui flottent toutes est une page sans hiérarchie.

---

## 7. Bordures

| Usage | Valeur |
|---|---|
| Bordure standard | `1px solid --neutre-200` |
| Bordure marquée (séparation forte) | `1px solid --neutre-300` |
| Bordure de champ au focus | `1px solid --solida-teal-800` + anneau `2px --solida-teal-100` |
| Bordure d'erreur | `1px solid --decision-refus` |

Jamais de bordure de plus de 1 px, sauf la barre latérale colorée d'un bloc de décision (3 px).

---

## 8. Focus et accessibilité visuelle

L'anneau de focus est **toujours visible au clavier**, jamais supprimé.

```
outline: 2px solid var(--solida-teal-600);
outline-offset: 2px;
```

Contraste minimal : 4,5:1 pour le texte courant, 3:1 pour les éléments d'interface. Les couleurs
ci-dessus ont été choisies pour satisfaire ce critère sur fond blanc et sur leur fond associé.

**Jamais d'information portée par la seule couleur.** Une tranche de décision porte toujours un
libellé écrit en plus de sa couleur.

---

## 9. Mise en page

- Largeur maximale de contenu : 1440 px, centré.
- Grille de 12 colonnes, gouttière 16 px.
- Barre d'en-tête fixe de 56 px : logo, recherche globale, agence, utilisateur.
- Pas de barre latérale permanente : l'agent a un parcours, pas une navigation à explorer.
  La navigation secondaire tient dans l'en-tête.
- Point de rupture unique à 1024 px. En dessous, mise en page à une colonne. Le poste cible est un
  ordinateur de bureau ; le responsive sert au confort, pas à un usage mobile.

---

## 10. Finition premium — la couche qui fait la différence

Les jetons ci-dessus donnent une interface correcte. Ce qui sépare une interface *correcte* d'une
interface *primée* tient dans une poignée de détails de finition, invisibles pris un par un, décisifs
pris ensemble. Cette section les rend obligatoires, sans ajouter ni couleur, ni ombre, ni animation
au-delà de ce qui précède : le premium vient de la **précision**, pas de l'ajout.

### 10.1 Un seul moment de héros par parcours

Toute l'attention visuelle d'un parcours converge vers **un unique point fort** : le score, sur
l'écran de résultat. C'est le seul endroit où l'on emploie `texte-score` (56 px), le compteur animé
(#4 du motion) et la barre de position synchronisée. Partout ailleurs, l'interface est calme et
plate. Un deuxième moment spectaculaire tuerait le premier. **La retenue ailleurs est ce qui donne
son poids au score.**

### 10.2 Rythme typographique et alignement optique

- Tous les chiffres comparables (montants en colonne, scores, taux) sont en `tabular-nums` : une
  colonne de montants s'aligne au chiffre près, sans quoi l'ensemble paraît amateur.
- Le score, centré optiquement et non mathématiquement dans son bloc : un grand nombre en Plex Mono
  doit être calé à l'œil, l'optique prime sur le calcul de centre.
- Une seule échelle de gris pour le texte (`neutre-950 / 700 / 500`) : trois niveaux de gris, pas
  cinq. La hiérarchie se lit par la taille et la graisse, pas par une palette de gris.

### 10.3 Le calme comme signature (esprit tableau de bord)

L'écran d'accueil et le dossier 360° doivent respirer sans se vider : **dense mais ordonné**. La
règle : chaque zone a un rôle unique et un seul, séparée des autres par une bordure `neutre-200` et
un fond, jamais par une ombre. Aucun élément ne « flotte ». Le regard entre par le haut à gauche,
descend en Z, et ne rencontre jamais deux accents or en concurrence. Un tableau de bord premium se
reconnaît à ce qu'on sait **où regarder en premier** sans effort — c'est une propriété de mise en
page, pas de décoration.

### 10.4 Craftsmanship des états

Ce sont les états secondaires qui trahissent une interface bâclée ; ils sont ici traités avec le
même soin que l'état nominal.

| État | Exigence de finition |
|---|---|
| Vide | Une phrase utile qui dit quoi faire, jamais une illustration décorative ni un « aucune donnée » sec. L'état vide du primo-emprunteur est formulé comme une information, pas comme un manque |
| Chargement | Squelette aux dimensions exactes du contenu à venir (pas un spinner centré), frémissement discret, jamais une pulsation marquée |
| Focus clavier | Anneau `teal-600` visible, offset 2 px, **jamais supprimé** — un parcours entièrement navigable au clavier est un marqueur de sérieux que les jurys techniques vérifient |
| Survol de ligne | Fond `neutre-50`, transition couleur 120 ms, sans déplacement ni ombre |
| Erreur de champ | Bordure `refus` + message texte sous le champ, jamais la seule couleur |

### 10.5 Densité juste

La densité imposée (§4) sert la vitesse d'un poste utilisé cent fois par jour, mais la densité n'est
pas l'entassement : entre deux blocs de rôles différents, on laisse 24 px ; à l'intérieur d'un bloc,
8 à 12 px. Le rythme d'espacement — serré à l'intérieur, aéré entre les groupes — est ce qui fait
qu'un écran dense reste lisible. C'est la différence entre un cockpit et un fouillis.

### 10.6 Ce qu'un juré de design retiendra

Si l'interface est réussie, le juré ne remarquera aucun de ces détails isolément. Il retiendra une
impression d'ensemble : **un outil calme, rapide, sûr de lui, où chaque pixel a une raison d'être**,
qui ne ressemble ni à un CRM générique ni à une démonstration générée. C'est exactement l'inverse de
l'effet « waouh » tape-à-l'œil — et c'est ce qui gagne dans la catégorie des outils métier.
