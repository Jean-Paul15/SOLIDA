# Accessibilité

Cible : **WCAG 2.1 niveau AA**. Ce n'est pas un objectif décoratif. Un agent de crédit peut avoir
une vue fatiguée, un écran de mauvaise qualité, un éclairage difficile, et travaille vite.

## Règles non négociables

| Règle | Vérification |
|---|---|
| Contraste texte ≥ 4,5:1 | Palette conçue pour, à revérifier sur toute nouvelle couleur |
| Contraste éléments d'interface ≥ 3:1 | Bordures, icônes, barres |
| Focus toujours visible au clavier | `:focus-visible` avec anneau 2 px, jamais `outline: none` |
| Parcours principal 100 % clavier | Recherche → dossier → demande → score, sans souris |
| Ordre de tabulation = ordre visuel | Pas de `tabindex` positif |
| Information jamais portée par la seule couleur | Toute tranche a un libellé écrit |
| Champs étiquetés | `<label>` associé, jamais un simple placeholder |
| Erreurs annoncées | `aria-invalid`, `aria-describedby`, région `role="alert"` |
| `prefers-reduced-motion` respecté | Toutes les animations désactivables |
| Taille de cible ≥ 24 px | Y compris les icônes cliquables |

## Points spécifiques à SOLIDA

**Le score doit être annoncé correctement par un lecteur d'écran.** Un grand nombre isolé n'a pas
de sens vocalisé. L'élément porte un libellé accessible complet : « Score 586 sur 850, tranche
accord sous condition, montant recommandé 875 000 francs CFA ».

**Le graphique de contributions doit avoir un équivalent textuel.** Une table masquée
visuellement mais accessible reprend libellé, valeur et points. Un graphique inaccessible est un
graphique inutilisable pour l'audit.

**Le tableau du groupe de caution (E5) est un tableau HTML natif**, pas un rendu graphique : il est
nativement accessible au lecteur d'écran, sans équivalent alternatif à maintenir séparément.

**La liste de suggestions suit le motif combobox ARIA** : `role="combobox"`, `aria-expanded`,
`aria-activedescendant`, `role="listbox"` et `role="option"`. Le composant `Command` de shadcn le
fait déjà correctement, ce qui est une raison de plus de ne pas le réimplémenter.

## Ce qui est vérifié avant de considérer un écran terminé

1. Parcourir l'écran uniquement au clavier, du premier au dernier élément.
2. Vérifier que le focus est visible à chaque étape.
3. Zoomer à 200 % : aucun contenu ne doit être coupé ni nécessiter un défilement horizontal.
4. Simuler la désactivation des animations.
5. Passer un contrôle automatique (axe) : zéro violation critique.
