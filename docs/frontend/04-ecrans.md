# Écrans livrés

| Écran | Route | Composant principal |
|---|---|---|
| E0 Connexion | `/connexion` | `FormulaireConnexion` |
| E1 Recherche | `/` | `RechercheSocietaire` |
| E2 Dossier | `/societaires/[id]` | `app/societaires/[id]/page.tsx` |
| E3 Nouvelle demande | panneau sur E2 | `NouvelleDemandeSheet` |
| E4 Résultat scoring | `/scoring/[id]` | `app/scoring/[id]/page.tsx` |

## Simplifications connues

- **Bande des 12 mois (E2)** : les fixtures ne portent qu'un compteur agrégé
  (`nb_mois_avec_depot_12m`), pas un drapeau dépôt/mois. La bande remplit les N premiers mois
  plutôt que les mois réels — l'intitulé chiffré reste exact.
- **Graphique de contributions (E4)** : implémenté avec Recharts sous une forme à deux colonnes
  (libellé + valeur combinés à gauche, points à droite), pas trois colonnes distinctes comme la
  maquette texte le montre — l'information est complète, la mise en page diffère légèrement.
- **Décalage de 25 ms par ligne** sur l'apparition des barres n'est pas implémenté à l'unité près ;
  l'apparition du graphique est animée une seule fois, globalement.
- **Épargne disponible (E2, hors segment groupement)** remplace « Épargne nantie » : le contrat gelé
  ne porte pas de champ « montant nanti ». Voir `02-contrats-et-mocks.md`.
- **Écran E5** (groupe de caution) n'existe pas dans cette passe (P1) : le lien correspondant a été
  retiré d'E2 plutôt que de pointer vers une route inexistante.
