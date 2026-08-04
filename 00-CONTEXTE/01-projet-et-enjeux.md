# Projet et enjeux

## Le problème

Dans les coopératives financières d'Afrique de l'Ouest, l'octroi de microcrédit repose sur une
instruction manuelle. Trois conséquences :

- **Décisions hétérogènes** : à dossier comparable, deux agents décident différemment.
- **Délais élevés** : jours ou semaines entre le dépôt et la décision.
- **Impayés** : au Togo, le taux brut de dégradation du portefeuille des IMF est passé de 4,2 % en
  2022 à 7,8 % en 2024, puis 6,7 % en 2025, contre une norme BCEAO de 3 %.

Cause commune : l'information décisive existe déjà dans le système de gestion de la coopérative,
mais elle n'est ni consolidée ni exploitée.

## La proposition

SOLIDA est un **système de scoring d'octroi**, pas un modèle isolé. Il transforme les données déjà
détenues par la coopérative en score de risque, recommandation de montant, plafond de crédit
progressif et fiche de justification actionnable, restitués à l'agent de crédit en moins d'une
minute.

Sa spécificité est de placer au centre ce qui existe pour **100 % du portefeuille** : la trajectoire
d'épargne, porte d'entrée du crédit dans le modèle mutualiste, et le comportement de remboursement.
Cette donnée est enregistrée depuis toujours ; elle n'est simplement pas exploitée comme signal de
risque. SOLIDA l'enrichit, sur le seul segment des crédits de groupe, par l'historique de la caution
solidaire.

**Position dans la trajectoire de digitalisation de la CIF.** Le projet DigiCoop-WA a déjà digitalisé
la collecte de l'épargne et l'octroi de crédit dans les réseaux membres, sur le socle applicatif
unique SAB-AT (dépôt et retrait à distance, opérations en temps réel dans les six fédérations).
SOLIDA n'ajoute aucune infrastructure : c'est la couche de décision qui exploite la donnée que le
réseau a déjà centralisée et digitalisée. C'est le prolongement naturel de DigiCoop-WA vers
DigiCoop-WA+, pas un projet parallèle.

## Des segments calqués sur les populations que la CIF cible déjà

La CIF se définit elle-même comme un acteur au service de « femmes, jeunes, petits exploitants
agricoles, entrepreneurs, commerçants, salariés ». Le générateur et le modèle SOLIDA reprennent
exactement cette segmentation (salarié, individuel, jeune primo-accédant, groupement de femmes,
agricole) plutôt qu'une typologie inventée : chaque segment porte un risque et un traitement
distincts, et la couche solidaire s'active précisément là où la CIF la pratique déjà — les
groupements de femmes.

## Les trois contraintes permanentes

Toute décision technique se juge à l'aune de ces trois points. Ils ne sont pas négociables.

### 1. Légèreté
Les coopératives visées ont une connectivité limitée, des volumes modestes et de faibles ressources
informatiques. Conséquences : pas de GPU, pas de dépendance à un service cloud propriétaire,
fonctionnement sur un serveur modeste, dégradation gracieuse en cas de coupure.

### 2. Explicabilité
Le demandeur est un **sociétaire**, pas un client anonyme. Un refus non expliqué dégrade la relation
de proximité qui fonde le modèle coopératif. Toute décision doit être justifiable variable par
variable, en langage accessible.

### 3. Souveraineté
Les données restent la propriété de la coopérative et ne quittent pas son périmètre. Aucun appel
sortant vers un service tiers avec des données de sociétaire.

## Ce que SOLIDA n'est pas

| SOLIDA n'est pas… | Pourquoi c'est important |
|---|---|
| Un système de décision automatique | L'agent et le comité conservent le pouvoir de décision |
| Un modèle de suivi de portefeuille (IFRS 9, staging) | On score à l'octroi, pas en cours de vie du crédit |
| Un système de détection de fraude | C'est la Thématique 01, hors de notre périmètre |
| Un core banking | Nous lisons le SI de l'IMF, nous ne le remplaçons pas |
| Un produit dépendant du mobile money | Aucun accès Flooz / Mixx by Yas à court terme |

## Critères de notation du hackathon

Toute arbitrage produit doit servir au moins un de ces critères.

| Critère | Poids | Ce qui le sert dans SOLIDA |
|---|---|---|
| Pertinence et adéquation à la thématique | 30 % | Données déjà détenues par l'IMF, contraintes terrain respectées |
| Originalité et caractère innovant | 20 % | Trajectoire d'épargne dynamique comme signal central ; crédit progressif et fiche actionnable ; renoncement argumenté aux mesures de graphe inadaptées à ce contexte |
| Faisabilité technique et réalisme | 20 % | Aucune dépendance externe, architecture en cascade, MVP priorisé |
| Impact pour les coopératives membres CIF | 15 % | Déployable sans négociation contractuelle, standard d'intégration |
| Complémentarité de l'équipe | 15 % | Hors périmètre technique |

## Références de calibrage

| Donnée | Valeur | Source |
|---|---|---|
| Taux de dégradation portefeuille Togo 2025 | 6,7 % | Ministère des Finances / APSFD-Togo |
| Norme BCEAO | 3 % | BCEAO |
| Encours moyen par client UEMOA | < 140 000 FCFA | BCEAO |
| Plafond taux d'usure SFD | 24 % TAEG depuis le 01/06/2026 | Décision n°19/29-12-2025/CM/UMOA |
| Nombre de SFD agréés au Togo | 63 à 72 selon la source et la date | Ministère des Finances |

## Le réseau CIF, en bref

La Confédération des Institutions Financières d'Afrique de l'Ouest (CIF) regroupe six grandes
faîtières coopératives dans cinq pays de l'UEMOA : Bénin, Burkina Faso, Mali, Sénégal, Togo. Au
Togo, la faîtière est FUCEC-TOGO. Le réseau totalise plusieurs millions de membres et vise, à
l'horizon 2035, à être l'acteur de référence de l'inclusion financière et de l'innovation en
Afrique de l'Ouest.

Point déterminant pour SOLIDA : la CIF exploite depuis 2020 un Système Unique d'Information (SIG)
qui connecte ses six faîtières. C'est la cible d'intégration privilégiée (voir
`02-DONNEES/04-contrat-integration.md`) et un argument fort de déployabilité à l'échelle du réseau.

Toutes les données de SOLIDA sont synthétiques ; les chiffres du réseau servent au calibrage et à
l'argumentaire, pas à un traitement de données réelles.
