# Catalogue des composants

Composants spécifiques à SOLIDA, construits sur shadcn/ui. Chacun est écrit **une fois**, dans
`ui/`, et réutilisé. Un composant recréé localement dans un écran est un défaut de revue.

---

## Primitives adaptées (shadcn ajusté)

| Composant | Ajustements par rapport au défaut shadcn |
|---|---|
| `Button` | Hauteur 36 px, rayon 6 px, **ombre supprimée**, variantes : `principal`, `secondaire`, `tertiaire`, `danger` |
| `Input` | Hauteur 36 px, bordure 1 px, anneau de focus teal |
| `Card` | Ombre supprimée, bordure `--neutre-200`, rayon 8 px, padding 16 px |
| `Table` | Ligne 40 px, en-tête `texte-xs` majuscules `--neutre-500`, séparateurs 1 px |
| `Badge` | Hauteur 20 px, rayon 4 px, `texte-xs`, pas de dégradé |
| `Dialog` | Élévation 2, rayon 8 px |
| `Select` | Hauteur 36 px, panneau en élévation 1 |

---

## Composants métier

### `RechercheSocietaire`
Le composant central. Fondé sur `Command`.
- Props : `onSelection(societaire)`, `autoFocus`, `placeholder`
- Gère : différé 250 ms, navigation clavier, mise en gras de la correspondance, cinq états
- Ne gère pas : la navigation. Elle est du ressort de l'écran appelant

### `AffichageScore`
- Props : `score`, `tranche`, `montantRecommande`, `montantDemande`, `modeCalcul`
- Rend : le bloc de décision complet avec barre de position et compteur
- Respecte `prefers-reduced-motion`

### `BarreTranches`
- Props : `score`, `seuils`
- Rend : barre horizontale de 6 px, quatre segments colorés, repère de position
- Aucun texte à l'intérieur : les libellés sont en dessous

### `GraphiqueContributions`
- Props : `contributions`, `pointsDeBase`, `scoreTotal`
- Rend : barres divergentes + ligne de vérification arithmétique
- Tri, troncature à 8 et repli des suivantes gérés en interne

### `LigneContribution`
- Props : `contribution`
- Rend : libellé, valeur réelle, barre, points signés
- Infobulle au survol portant le champ `explication`

### `SyntheseEpargne`
- Props : `soldes12Mois`, `moisAvecDepot`
- Rend : chiffre principal, courbe Recharts, bande des 12 carrés mensuels

### `TableauHistoriqueCredit`
- Props : `credits`
- Rend : tableau dense avec badges de statut et coloration du retard
- État vide dédié pour le primo-emprunteur, formulé sans dramatisation

### `CarteGroupe`
- Props : `groupe | null`
- Rend : synthèse du groupe, ou état vide neutre si absence de groupe

### `TableauGroupeCaution`
- Props : `groupe`, `societaireCourantId`
- Rend : tableau des membres (composant `Table` de shadcn), ligne du sociétaire courant en
  surbrillance — pas de rendu SVG, pas de disposition à calculer
- État vide dédié si le groupe n'a pas encore d'historique de remboursement résolu

### `IndicateurFraicheur`
- Props : `date`
- Rend : « Données consolidées le … à … », `texte-xs`, `--neutre-500`

### `BandeauModeCalcul`
- Props : `mode`, `motif`
- Rend : icône + phrase explicative en français, sans vocabulaire technique

### `MontantFCFA`
- Props : `valeur`, `taille`
- Rend : formatage unique et centralisé, chiffres tabulaires
- **Aucun autre endroit du code ne formate un montant**

### `EtatVide`
- Props : `titre`, `description`, `action?`
- Rend : bloc d'état vide homogène dans toute l'application

### `EtatErreur`
- Props : `message`, `onReessayer`
- Rend : cause en français + bouton de reprise

---

## Conventions de code front

| Règle | Détail |
|---|---|
| Server Components par défaut | `"use client"` seulement si état local, effet ou événement |
| Pas de `fetch` dans un composant | Les appels passent par `services/api` |
| Pas de `any` | Types dérivés des contrats de `01-ARCHITECTURE/05` |
| Pas de valeur de style en dur | Uniquement des classes issues des jetons |
| Un composant par fichier | Nom du fichier = nom du composant |
| Props typées explicitement | Pas d'inférence implicite sur une signature publique |
| Pas de `localStorage` pour des données métier | Uniquement préférences d'affichage |

---

## Arborescence front

```
frontend/
├── app/
│   ├── (auth)/connexion/
│   ├── (app)/
│   │   ├── page.tsx                    E1 Recherche
│   │   ├── societaires/[id]/           E2 Dossier
│   │   ├── scoring/[id]/               E4 Résultat
│   │   ├── registre/                   E7
│   │   └── parametrage/                E8, E9
│   └── layout.tsx
├── domain/
│   ├── types.ts                        Types issus des contrats
│   ├── formatage.ts                    Montants, dates, durées
│   └── tranches.ts                     Libellés et couleurs de tranche
├── services/
│   ├── client.ts                       Client HTTP, gestion d'erreur, auth
│   ├── societaires.ts
│   └── scoring.ts
├── ui/
│   ├── primitives/                     shadcn ajusté
│   └── metier/                         Composants du catalogue ci-dessus
└── styles/
    └── theme.css                       Jetons Tailwind 4 via @theme
```
