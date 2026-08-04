# Contrats et implémentations factices

## Fichiers

| Fichier | Rôle |
|---|---|
| `frontend/lib/contracts.ts` | Types TypeScript des structures consommées par le front |
| `frontend/lib/mocks/societaires.ts` | Six dossiers fixtures couvrant les cas de test standards |
| `frontend/lib/mocks/agents.ts` | Identifiants de démonstration pour la connexion |
| `frontend/lib/mocks/scoring.ts` | Moteur de scoring factice, déterministe |
| `frontend/lib/session.ts` | Cookie de session (httpOnly, sameSite=lax) |
| `frontend/app/api/v1/**` | Endpoints P0, implémentés en Route Handlers Next.js |

## Cas fixtures

| Identifiant | Cas |
|---|---|
| `soc-adjo` | Salarié, deux crédits dont un en cours, aucun incident |
| `soc-kossi` | Primo-emprunteur, individuel, aucun historique de crédit |
| `soc-akossiwa` | Groupement, groupe sain (97 % de remboursement), 3 cycles complétés |
| `soc-mawuli` | Groupement, groupe dégradé (61 %), incident en cours, caution appelée |
| `soc-koffi` | Individuel, revenu déclaré absent (donnée incomplète) |

Toutes les identités sont inventées ; aucune ne correspond à une personne réelle.

## Écart avec le contrat gelé — résolu (ADR-019)

`age`, `niveau_instruction`, `nb_personnes_a_charge` et `parts_sociales_montant` ont été ajoutés à
`IdentiteSocietaire`/`ActiviteEconomique` (présents dans le générateur, attendus par l'écran E2,
absents avant correction). La carte « Profil » de l'écran E2 les affiche désormais. Le statut du
logement reste absent : il n'existe dans aucune source (ni contrat, ni générateur) — non affiché.

## Moteur de scoring factice

`calculerScoring` produit une décomposition cohérente (la somme des points égale le score) à partir
des données des fixtures, sans aucun modèle entraîné — l'équivalent frontend d'un modèle constant.
Les seuils de tranche (700/600/500) sont des valeurs de travail, pas la grille réelle. Le résultat
est conservé en mémoire côté serveur (process Node), le temps de la session de développement, pour
que l'écran de fiche puisse le relire.

## Authentification de démonstration

`agents.ts` contient deux paires identifiant/mot de passe en clair, utilisées uniquement pour
exercer l'écran de connexion. Ce n'est pas une authentification réelle : à remplacer entièrement par
l'auth du backend. La session est un cookie signé de façon triviale (base64), pas un JWT — suffisant
pour développer le front, pas pour la production.
