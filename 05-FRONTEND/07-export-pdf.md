# Export PDF de la fiche de justification

## Décision : génération côté serveur

La fiche de justification est un **document opposable** : il est remis au sociétaire, archivé, et
peut être produit en cas de contestation. Il doit donc être identique quel que soit le poste, le
navigateur ou la version, et être archivé tel qu'il a été remis.

| Option | Retenue | Motif |
|---|---|---|
| Impression navigateur (CSS `@media print`) | Non, sauf en secours | Rendu variable selon navigateur, pas d'archivage |
| Génération client (`jsPDF`, `html2canvas`) | Non | Rendu approximatif, typographie française dégradée, poids |
| **Génération serveur HTML + CSS → PDF (WeasyPrint)** | **Oui** | Rendu déterministe, typographie correcte, archivable |

**Chaîne retenue :** un gabarit HTML + CSS rendu côté backend Python par WeasyPrint, produisant un
PDF archivé dans MinIO et servi par l'API.

Avantage secondaire non négligeable : le gabarit HTML réutilise les mêmes jetons de couleur et de
typographie que l'application. Le document et l'écran sont cohérents sans double maintenance.

---

## Contenu de la fiche

Une page A4. Jamais deux.

### En-tête
- Logo de la coopérative à gauche, logo SOLIDA discret à droite
- Titre : « Fiche de justification de décision de crédit »
- Référence du dossier, date et heure d'édition

### Bloc identité
Sociétaire, numéro de membre, agence, agent instructeur.

### Bloc demande
Produit, montant sollicité, durée, objet.

### Bloc résultat
Score, tranche en toutes lettres, montant recommandé. Encadré avec la bordure gauche de couleur
sémantique, comme à l'écran.

### Bloc trajectoire de progression
Les plafonds accessibles sur les 3 prochains cycles en cas de remboursement sans incident — reprise
directe de `ResultatScoring.trajectoire_progression`. Rend visible que la fiche n'est pas qu'un
verdict, même en cas de refus.

### Bloc facteurs
Deux colonnes :
- **Éléments favorables** : 3 à 5 lignes, libellé + valeur + phrase d'explication
- **Points de vigilance** : 3 à 5 lignes, même structure

Les points chiffrés **n'apparaissent pas** dans la fiche remise au sociétaire. Ils sont pertinents
pour l'agent et l'audit, pas pour le demandeur, à qui l'on doit une explication en langage clair.
Une variante « fiche interne » avec les points est générée pour le dossier.

### Bloc conditions de réexamen
Uniquement en cas de refus ou d'accord conditionnel. Trois formulations maximum, concrètes :
« Une régularité d'épargne d'au moins 9 mois sur 12 permettrait de reconsidérer la demande. »

### Pied de page
- Mention : « Ce document présente les éléments ayant fondé la recommandation du système d'aide à
  la décision. La décision finale relève de l'agent de crédit et du comité de crédit de la
  coopérative. »
- Versions du modèle et de la grille, en très petit — indispensable pour l'audit
- Numéro de page

---

## Contraintes de mise en forme

| Élément | Règle |
|---|---|
| Format | A4 portrait, marges 18 mm |
| Polices | IBM Plex Sans et IBM Plex Mono, **embarquées** dans le PDF |
| Couleurs | Jetons du design system, aplats uniquement |
| Graphiques | Aucun graphique Recharts. Les barres de facteurs sont dessinées en CSS |
| Poids | < 300 Ko |
| Métadonnées | Titre, auteur (nom de la coopérative), date de création, pas de logiciel tiers exposé |

---

## Cycle de vie

1. L'agent demande la fiche depuis E4.
2. Le backend assemble `FicheJustification` à partir de la décision **persistée**, jamais à partir
   d'un recalcul. Une fiche doit refléter la décision telle qu'elle a été rendue.
3. WeasyPrint produit le PDF.
4. Le PDF est déposé dans MinIO sous une clé stable : `fiches/{annee}/{mois}/{fiche_id}.pdf`.
5. L'API renvoie une URL signée à durée limitée.
6. L'événement est journalisé dans le registre d'audit.

**Immuabilité :** une fiche générée n'est jamais régénérée ni écrasée. Si la décision est revue,
une nouvelle fiche est créée avec un nouvel identifiant, et l'ancienne est conservée.

---

## Repli

Si MinIO est indisponible, le PDF est renvoyé directement dans la réponse HTTP sans archivage, et
un avertissement est journalisé. L'agent n'est jamais bloqué par une panne de stockage — c'est une
application du principe de dégradation gracieuse.
