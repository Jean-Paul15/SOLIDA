# Design system — implémentation

## Fichiers

| Fichier | Rôle |
|---|---|
| `frontend/app/globals.css` | Bloc `@theme` Tailwind v4 : toutes les couleurs, l'échelle typographique, les rayons, les deux niveaux d'ombre. Source unique — aucune valeur codée en dur ailleurs |
| `frontend/app/fonts.ts` | IBM Plex Sans (400/500/600), IBM Plex Mono (400/500), Source Serif 4 (600, titres d'écran uniquement) via `next/font/google` — auto-hébergées, aucune requête sortante vers Google au runtime |
| `frontend/app/layout.tsx` | Injecte les variables de police sur `<body>` |

## Décisions d'implémentation

- **Espacement** : aucune surcharge Tailwind — l'échelle par défaut (`p-1`=4px … `p-12`=48px)
  correspond déjà au pas de 4 px imposé. Seules les classes correspondant aux valeurs autorisées
  (4/8/12/16/20/24/32/40/48) doivent être utilisées dans les composants.
- **Échelle typographique** : les tailles sont portées par les clés Tailwind natives
  (`text-xs`…`text-score`), pas de renommage en français des utilitaires.
- **Élévation** : niveau 0 = `border border-neutre-200` sans ombre (classe par défaut) ; niveaux 1
  et 2 = utilitaires `shadow-1` / `shadow-2` définis dans `@theme`.
- **Mode sombre** : absent, aucun `dark:` nulle part.
- **Focus clavier** : anneau `teal-600` appliqué globalement via `:focus-visible`, jamais supprimé.
- **shadcn/ui** : les jetons sémantiques du système (`background`, `primary`, `border`, `ring`…)
  sont remappés une seule fois dans `globals.css` (bloc `@theme inline`) sur les couleurs SOLIDA
  ci-dessus, plutôt que composant par composant. Aucune variante sombre n'est déclarée.

## Ajouter un nouveau jeton

Toujours dans `app/globals.css`, dans le bloc `@theme`. Ne jamais écrire une couleur, une taille ou
un rayon ailleurs — y compris dans un composant shadcn ajusté.
