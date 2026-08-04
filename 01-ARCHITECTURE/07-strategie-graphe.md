# Stratégie de la couche solidaire

*Anciennement « Stratégie graphe ». Renommé par ADR-016 : voir `00-CONTEXTE/04-journal-de-decisions.md`.*

## Décision de fond

Le crédit de groupe (caution solidaire) est un **segment** du portefeuille d'une coopérative
d'épargne et de crédit — typiquement les groupements de femmes et certains financements agricoles
— et non son cœur, qui reste le crédit individuel adossé à l'épargne. La couche solidaire de SOLIDA
en tire une conséquence directe : **pas de base de données graphe, pas de métrique de centralité,
pas de propagation de réputation.** Ce n'est pas une simplification par manque de temps : c'est que
la densité de réseau qu'exigeraient ces outils n'existe pas ici.

Ce que produit la couche solidaire : trois agrégats simples, calculés sur les crédits et garanties
du segment de groupe, hors du sociétaire évalué.

## Pourquoi pas de base de données graphe

| Option | Écartée parce que |
|---|---|
| Neo4j, Apache AGE | Un service ou une extension de plus à exploiter pour une structure qui, empiriquement, reste petite et clairsemée sur ce portefeuille |
| Mesures de centralité (betweenness, PageRank) | Supposent un réseau dense d'interconnexions. Un portefeuille dominé par le crédit individuel n'en produit pas. Les calculer reviendrait à extraire un signal d'une structure qui n'existe pas |
| Agrégats de groupe en SQL classique | **Retenu.** Un `GROUP BY` sur les crédits d'un groupe suffit ; aucune infrastructure supplémentaire |

Ordre de grandeur réaliste sur un portefeuille coopératif : la majorité des garanties sont de
l'**épargne nantie** (garantie réelle, pas un lien interpersonnel) ; les crédits de groupe
représentent de l'ordre de 15 à 20 % du portefeuille. Bâtir une infrastructure de graphe pour ce
volume, avec cette densité, serait une décision d'affichage, pas d'ingénierie — et un mentor
technique le relèverait.

## Ce qui est calculé

### Sources

| Table | Rôle |
|---|---|
| `groupe_caution` (GIE) | Groupe de crédit solidaire — segment, pas la population générale |
| `appartenance_groupe` | Qui appartient à quel groupe, avec historique d'entrée/sortie |
| `garantie` | Porte le type (`epargne_nantie` ou `caution_solidaire_gie`) et l'indicateur d'appel |

### Agrégats de la couche solidaire

| Variable | Calcul | Intuition métier |
|---|---|---|
| `taux_remboursement_groupe` | Part des crédits du groupe soldés sans incident, **hors sociétaire évalué**, avant la date de référence | Réputation collective — la responsabilité conjointe rend les défauts d'un même groupe corrélés |
| `taille_groupe` | Membres actifs à la date de référence | Un groupe plus grand dilue et discipline mieux le risque individuel |
| `deja_secouru_par_groupe` | Une garantie a-t-elle déjà été appelée au profit de ce sociétaire | Signal individuel fort, disponible si `garantie_appelee` est tracé |

**Le retrait du sociétaire évalué du calcul de `taux_remboursement_groupe` est impératif.** Sans
cela, on lui prédit son propre défaut et le modèle paraît excellent avant de s'effondrer.

### Fenêtre temporelle

**Règle absolue anti-fuite :** ces agrégats ne retiennent que les crédits du groupe **résolus avant
la date de la demande évaluée**. Un calcul sur l'état final de la base ferait fuiter l'information
future dans le passé et produirait des performances irréalistes qui s'effondreraient en production.
Chaque calcul prend un paramètre `date_reference` obligatoire.

## Traitement des cas dégénérés

| Cas | Comportement |
|---|---|
| Sociétaire hors segment de groupe (immense majorité) | Toutes les variables solidaires à `null`, mode `socle_seul` — c'est l'état normal, pas une exception |
| Groupe sans historique de crédit résolu | `taux_remboursement_groupe` à `null`, pas à 0 ni à 1 |
| Groupe d'un seul membre restant | Traité comme hors segment |

**`null` n'est pas 0.** Un groupe sans historique n'est ni bon ni mauvais. Confondre absence
d'information et information négative est l'erreur classique du scoring relationnel, et elle
pénaliserait systématiquement les groupes récents.

## Persistance

- Les **tables brutes** (`groupe_caution`, `appartenance_groupe`, `garantie`) sont copiées depuis
  CORE-SIM par le batch, avec leurs dates de validité.
- Les **agrégats calculés** par sociétaire et par date de référence sont écrits dans le feature
  store. Aucune structure de graphe n'est jamais matérialisée ni persistée.

## Affichage

L'écran de groupe de caution (module F5, voir `05-FRONTEND/04`) affiche une **liste plate** des
membres du groupe avec leur statut de remboursement — pas une visualisation en anneaux ni un rendu
de graphe à plusieurs degrés. Un groupe compte au plus une vingtaine de membres ; une liste triée
par ancienneté ou par statut se lit plus vite qu'un diagramme de nœuds, et n'introduit pas de fausse
impression de complexité relationnelle là où la structure réelle est simple.
