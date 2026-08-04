# Contrat d'intégration

C'est notre proposition de **standard d'interopérabilité** pour le réseau CIF, et l'argument
central de déployabilité : une coopérative dont le système de gestion couvre ces champs peut
alimenter SOLIDA par un simple export, sans refonte.

## Périmètre minimal

### Bloc 1 — Sociétaire (obligatoire)

| Champ | Type | Obligatoire |
|---|---|---|
| identifiant sociétaire | texte | oui |
| numéro de membre | texte | oui |
| nom complet | texte | oui |
| date d'adhésion | date | oui |
| date de naissance | date | oui |
| zone de résidence | énumération | oui |
| secteur d'activité | énumération | oui |
| ancienneté de l'activité (mois) | entier | recommandé |
| revenu mensuel déclaré | entier | recommandé |
| charges mensuelles | entier | recommandé |
| personnes à charge | entier | recommandé |
| parts sociales | entier | recommandé |
| agence | texte | oui |
| statut | énumération | oui |

### Bloc 2 — Épargne (obligatoire)

| Champ | Type |
|---|---|
| identifiant compte, identifiant sociétaire, type de compte | texte |
| date d'opération, sens, montant | date, énumération, entier |

Profondeur minimale exigée : **12 mois**. En deçà, la variable de régularité perd son sens.

### Bloc 3 — Crédit (obligatoire)

| Champ | Type |
|---|---|
| identifiant crédit, identifiant sociétaire | texte |
| montant octroyé, durée, date de déblocage, numéro de cycle | entier, entier, date, entier |
| statut, capital restant dû | énumération, entier |
| date d'échéance prévue, date de paiement, montant payé | date, date, entier |

Profondeur minimale : **24 mois**, idéalement 36.

### Bloc 4 — Couche solidaire (optionnel, segment de groupe, active le modèle enrichi)

| Champ | Type |
|---|---|
| identifiant groupe, nom, date de création | texte, texte, date |
| appartenance : groupe, sociétaire, date d'entrée, date de sortie | texte, texte, date, date |
| garantie : garant, bénéficiaire, crédit, montant, appelée | texte, texte, texte, entier, booléen |

**Sans ce bloc, SOLIDA fonctionne en mode socle uniquement.** C'est une dégradation prévue, pas un
blocage. Une IMF qui ne suit pas ses groupes de manière structurée peut quand même déployer.

## Le cas CIF : un Système Unique d'Information existant

La CIF a déployé, à partir de 2020, un Système Unique d'Information (SIG) qui connecte ses six
faîtières (FCPB au Burkina, FECECAM au Bénin, FUCEC-TOGO, Kafo Jiginew et NYESIGISO au Mali,
UM-PAMECAS au Sénégal) et centralise les données de plusieurs millions de membres. C'est un logiciel
de type bancaire adapté aux coopératives.

**Conséquence stratégique majeure :** la cible d'intégration de SOLIDA n'est pas six systèmes
hétérogènes, mais **ce SIG partagé**. L'argument devant le jury devient beaucoup plus fort :

> « SOLIDA se branche sur votre Système Unique d'Information existant. Une intégration, et le réseau
> entier en bénéficie, pas une intégration par coopérative. »

Le contrat ci-dessous reste valable tel quel : il définit les champs dont SOLIDA a besoin, que la
source soit le SIG de la CIF ou le système propre d'une coopérative hors réseau. La démonstration
s'ancre sur une coopérative de type FUCEC-TOGO, puisque le hackathon a lieu à Lomé.

## Modes d'intégration, par ordre de préférence

| Mode | Description | Quand |
|---|---|---|
| 0. Branchement sur le SIG CIF | Vue en lecture ou export depuis le Système Unique d'Information | **Cas de référence pour le réseau CIF** |
| 1. Vue en lecture seule | Vues SQL exposant les champs dans la base du SI | Coopérative hors SIG dont l'éditeur l'autorise |
| 2. Export périodique | CSV ou Parquet déposés dans un répertoire, ingérés par le batch | **Cas le plus universel** |
| 3. API | Le SI expose des endpoints | Rare dans les IMF isolées |

**Le mode 2 est celui à mettre en avant devant le jury.** Aucune IMF ne refuse un export nocturne ;
beaucoup refusent un accès direct à leur base de production.

## Règles de conformité

| Règle | Détail |
|---|---|
| Encodage | UTF-8 obligatoire |
| Dates | ISO 8601 |
| Montants | Entiers en FCFA |
| Valeurs manquantes | Champ vide, jamais `0`, jamais `N/A` |
| Identifiants | Stables dans le temps. Un identifiant réattribué casse tout l'historique |
| Volumétrie | Export complet ou incrémental par date de modification |

## Validation à l'ingestion

Le module `data.validation` refuse un lot non conforme et produit un rapport lisible par un
informaticien d'IMF, pas une trace technique. Contrôles : présence des colonnes obligatoires,
types, cohérence référentielle, profondeur d'historique, taux de valeurs manquantes par colonne
avec seuil d'alerte.

**Un lot partiellement invalide est rejeté en entier.** Ingérer partiellement produit un feature
store incohérent, plus dangereux qu'une absence de mise à jour.
