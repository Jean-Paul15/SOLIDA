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

`FicheJustification` (E6) : ajout de `demande` (l'`EntreeScoring` d'origine, nécessaire au « Bloc
demande » — produit, montant, durée, objet — spécifié par `07-export-pdf.md`) et `numero_membre`
(« Bloc identité »). Absents du contrat initial, qui ne prévoyait que le résultat et l'identité
sommaire.

## Moteur de scoring factice

`calculerScoring` produit une décomposition cohérente (la somme des points égale le score) à partir
des données des fixtures, sans aucun modèle entraîné — l'équivalent frontend d'un modèle constant.
Les seuils de tranche (700/600/500) sont des valeurs de travail, pas la grille réelle.

## Décision persistée par identifiant opaque (`decision_id`)

`ResultatScoring` porte désormais un `decision_id` (UUID généré à l'enregistrement). `POST
/api/v1/scoring` calcule et persiste la décision (`lib/mocks/decisions.ts`, `Map` accrochée à
`globalThis` — nécessaire car Turbopack en dev peut charger ce module dans plus d'une instance
selon le graphe routeur/page, ce qui viderait une `Map` locale entre l'écriture et la lecture),
puis renvoie le résultat complet incluant son `decision_id`. L'écran E4 (`/scoring/[id]`) prend
ce `decision_id` comme paramètre de route — jamais les paramètres de la demande (montant, durée,
objet) en clair dans l'URL.

**Pourquoi ce choix, pas des paramètres de requête** : mettre `montant_demande`, `duree_demandee_mois`
etc. dans l'URL (`?montant_demande=500000&...`) expose des données métier dans l'historique du
navigateur, les journaux serveur et tout lien partagé, et permettrait de rejouer un scoring en
modifiant les valeurs directement dans l'URL. Un identifiant opaque de décision déjà calculée et
immuable élimine les deux problèmes : l'URL ne référence qu'un résultat déjà figé, elle ne permet
pas de le falsifier. C'est aussi la forme que prendra l'intégration réelle : `decision_scoring`
(`02-DONNEES/02-schema-solida.md`) est déjà pensée comme une table en insertion seule, avec son
propre identifiant.

`NouvelleDemandeSheet` appelle `POST /api/v1/scoring` (via `lib/services/scoring.ts`, jamais de
`fetch` direct dans un composant) et navigue vers `/scoring/{decision_id}` une fois la décision
obtenue — pas de calcul spéculatif côté page de destination.

## Bascule vers le backend réel (task #33) — ce qui doit changer, et rien d'autre

**Frontière côté client** : tout appel réseau depuis un composant client passe par
`lib/services/*.ts` (`scoring.ts`, `societaires.ts`). Ces fichiers appellent des chemins relatifs
(`/api/v1/...`). Le jour où le backend réel existe, un simple `rewrites()` dans `next.config.ts`
vers `http://api:8000/api/v1/:path*` suffit : aucun composant n'a besoin de changer.

**Frontière côté serveur** : les Server Components qui importent `lib/mocks/*` directement
(`app/societaires/[id]/page.tsx`, `app/scoring/[id]/page.tsx`, `app/scoring/[id]/fiche/page.tsx`,
`app/registre/page.tsx`, `app/parametrage/grille/page.tsx`) devront remplacer cet import par un
appel `fetch` vers le backend. C'est la seule vraie réécriture ; elle est localisée à ces cinq
fichiers, pas dispersée dans l'arbre des composants.

**À retirer une fois le câblage vérifié bout en bout, pas avant** : `frontend/lib/mocks/**` et
`frontend/app/api/v1/**`. Rien d'autre ne référence ces dossiers directement.

**Installable, vérifié** : `npm ci` (donc `docker build --target deps`, sans cache) installe les
758 paquets sans erreur ni vulnérabilité. Aucune dépendance non résolue, aucun paquet natif
manquant.

## Authentification de démonstration

`agents.ts` contient deux paires identifiant/mot de passe en clair, utilisées uniquement pour
exercer l'écran de connexion. Ce n'est pas une authentification réelle : à remplacer entièrement par
l'auth du backend. La session est un cookie signé de façon triviale (base64), pas un JWT — suffisant
pour développer le front, pas pour la production.
