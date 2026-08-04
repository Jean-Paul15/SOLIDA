# Gouvernance des données — intégrée au système, automatique

## Principe

La gouvernance n'est pas un outil qu'on ajoute à côté, c'est un ensemble de règles **appliquées par
le système lui-même**. On refuse un catalogue lourd (OpenMetadata, DataHub, Amundsen) : ce serait un
service de plus à exploiter dans une coopérative, contraire à la légèreté. La gouvernance de SOLIDA
est **du code et des jobs**, pas une plateforme.

Cinq briques, toutes automatiques.

---

## Brique 1 — Lignage : d'où vient chaque décision

Toute décision doit être traçable jusqu'à la donnée brute qui l'a produite.

```
champ brut CORE-SIM  ──►  feature (date_reference)  ──►  contribution en points  ──►  score  ──►  décision
```

**Mise en œuvre :** `decision_scoring` conserve les **valeurs** des features utilisées, pas
seulement leurs identifiants (voir `02-schema-solida.md`). Le catalogue de features
(`03-MODELE/02`) documente pour chaque feature le ou les champs bruts dont elle dérive et la formule.
La chaîne complète est donc reconstituable pour n'importe quelle décision, des mois plus tard.

**Ce que ça permet :** répondre à un auditeur ou à un sociétaire « ce facteur vient de vos dépôts
d'épargne des 12 derniers mois, dont 11 mois avec au moins un dépôt », et le prouver.

---

## Brique 2 — Rétention et purge automatiques

Aucune donnée ne survit au-delà de sa durée de conservation. Ce n'est pas laissé à une décision
humaine, c'est un job.

| Donnée | Conservation | Action à échéance |
|---|---|---|
| Feature store | 24 mois glissants | Purge des lignes au-delà |
| Décisions de scoring | Durée légale des dossiers de crédit | Aucune purge avant échéance légale |
| Fiches PDF | Idem décisions | Conservées, immuables |
| Journal d'audit | 5 ans | Archivage puis purge |
| Journaux techniques | 90 jours | Rotation automatique |
| Instantanés de données | 6 mois, sauf liés à un modèle en production | Purge conditionnelle |

**Mise en œuvre :** un job batch `appliquer_retention` s'exécute chaque nuit, journalise ce qu'il
purge, et **ne touche jamais** une donnée liée à un modèle ou une décision encore susceptible d'être
contestée. La purge est réversible pendant 30 jours (corbeille logique) avant suppression définitive.

---

## Brique 3 — Classification et protection des données personnelles

Chaque colonne du système porte une étiquette, et cette étiquette a des conséquences mécaniques.

| Classe | Exemples | Conséquence appliquée par le système |
|---|---|---|
| `nominatif` | nom, numéro de membre | Jamais journalisé, jamais dans une réponse d'erreur, jamais exporté sans droit |
| `sensible` | sexe | **Exclu du modèle par un test bloquant**, réservé au contrôle de non-discrimination |
| `financier` | montants, soldes | Jamais journalisé associé à un nominatif |
| `technique` | identifiants opaques, dates | Libre |

**Mise en œuvre :** la liste des classes vit dans la configuration. Trois garde-fous automatiques :
1. Un test refuse l'entraînement si une colonne `sensible` apparaît dans les variables du modèle.
2. Le formateur de journaux masque toute valeur `nominatif` ou `financier` liée à un identifiant.
3. L'export du registre applique la classe selon le rôle qui exporte.

Ce qui n'est **pas** collecté du tout : appartenance ethnique, religieuse, opinions politiques,
données biométriques, santé (l'objet « urgence santé » est une catégorie de crédit, pas une donnée
médicale). Voir `08-SECURITE/02`.

---

## Brique 4 — Politiques d'accès centralisées

Qui voit quoi n'est pas dispersé dans le code, c'est déclaré à un seul endroit.

**Mise en œuvre :** une matrice rôle × ressource × opération, versionnée, appliquée par une
dépendance unique côté cas d'usage. Ajouter un droit se fait dans la matrice, jamais dans un `if`
au fond d'un routeur. Le cloisonnement par agence est une dimension de cette matrice.

Bénéfice : on peut présenter au jury **une seule table** qui dit exactement qui accède à quoi. C'est
ce qu'une inspection d'institution financière demande en premier.

---

## Brique 5 — Qualité en porte (data quality gate)

Une donnée non conforme n'entre pas. Trois niveaux, décrits dans `05-qualite-et-validation.md` :
structure (rejet du lot), cohérence (alerte), distribution (alerte).

**Outil retenu :** validation de schéma par **Pandera** (open source, léger, natif pandas) sur les
données à l'ingestion et à la sortie du calcul de features. Alternative si besoin de rapports plus
riches : **Great Expectations**, plus complet mais plus lourd — à n'adopter que si le temps le
permet. Par défaut : Pandera.

**Mise en œuvre :** chaque `DataFrame` qui entre dans le pipeline passe par un schéma Pandera qui
vérifie types, plages, non-nullité des clés, cardinalité des catégories. Un lot qui échoue est
**rejeté en entier**, jamais ingéré partiellement (un feature store à moitié à jour est plus
dangereux qu'un feature store périmé).

---

## Ce que la gouvernance produit, visible en démonstration

| Livrable | Où |
|---|---|
| Registre des décisions, filtrable et exportable | Écran E7 |
| Fiche de justification opposable | Écran E6, PDF |
| Matrice d'accès versionnée | Un fichier de configuration |
| Rapport de rétention (ce qui a été purgé et quand) | Journal du job batch |
| Rapport de qualité à chaque ingestion | Sortie du module `data.validation` |
| Preuve d'exclusion des variables sensibles | Test bloquant + rapport d'entraînement |

## Périmètre hackathon

**P0 :** brique 1 (lignage via `decision_scoring`), brique 3 (test bloquant sur variables sensibles,
masquage des journaux), brique 5 (Pandera à l'ingestion).
**P1 :** brique 4 (matrice d'accès centralisée), brique 5 étendue.
**P2 :** brique 2 (jobs de rétention automatiques), rapports.

La brique 1 et l'exclusion des variables sensibles doivent être en place **dès le premier scoring**,
sinon les décisions du jour 2 ne seront ni traçables ni défendables.
