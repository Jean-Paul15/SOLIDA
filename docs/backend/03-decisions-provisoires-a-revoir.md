# Décisions provisoires à revoir

Ce fichier est la référence unique pour tout ce qui, dans le backend, a été fixé arbitrairement
faute du vrai modèle entraîné ou d'un arbitrage métier définitif. Rien de ce qui suit n'est une
vérité figée : c'est un point de départ pour que la chaîne fonctionne dès maintenant.

## Le modèle lui-même

`ModeleConstant` renvoie une probabilité de défaut fixe (0,09 ; le taux de créances en souffrance
cible du générateur, pas une valeur inventée). **À remplacer entièrement** une fois le modèle réel
entraîné et calibré : c'est le seul changement attendu, aucun code au-dessus (scorecard, grille,
cascade, plafond progressif, persistance, HTTP) ne devrait avoir à changer, puisque tout dépend du
modèle uniquement via le port `ModeleScoring`.

## `ModeleConstant.contributions()` : décomposition factice, PAS apprise

Comme la probabilité est constante, le score et la décision ne dépendent jamais de cette méthode
(`scorer_demande.py` calibre `beta_0` pour absorber exactement l'écart). Elle sert uniquement à ce
que la fiche de justification et le graphique « Facteurs déterminants » affichent quelque chose de
plausible plutôt qu'une liste vide, en attendant le vrai modèle. Six variables (régularité
d'épargne, endettement, incidents, ancienneté, deux ratios d'épargne), des coefficients illustratifs
choisis à la main (même intuition de signe que `simulateur/config/config.yaml`, jamais ses valeurs).

**C'est la toute première chose à supprimer/remplacer dès qu'un vrai modèle (EBM entraîné) existe** :
`decomposer_en_points` (déjà câblé, `domain/rules/scorecard.py`) doit alors recevoir les vraies
contributions log-odds apprises, à la place de cette liste à la main. Rien d'autre en aval (mapper
HTTP, `GraphiqueContributions.tsx`, fiche PDF) n'a besoin de changer : ils affichent déjà
correctement n'importe quelle décomposition non vide.

## Paramètres de la scorecard (mise à l'échelle probabilité → score)

PDO = 20, score de référence = 600, rapport de référence = 50. Valeurs de travail cohérentes entre
elles, pas calibrées sur un vrai modèle. À recalibrer une fois la vraie distribution de probabilité
connue (un modèle mal calibré rend cette mise à l'échelle trompeuse).

## Paramètres de la grille de décision

`marge` (0,15) et `lgd` — perte en cas de défaut — (0,75), plus les multiplicateurs de zone (0,6 /
1 / 1,6). Ce ne sont pas des choix techniques : ils traduisent un arbitrage risque/approbation qui
appartient à la coopérative, pas à qui écrit le code. Les valeurs actuelles reprennent un prototype
de calcul (retiré du dépôt, voir `03-MODELE/09-lecons-prototype-simulateur.md`) qui a servi à
construire et tester le mécanisme — pas la vérité finale. Réglage
prévu par le superviseur (écran de paramétrage de la grille), affiné par le calibrage du modèle
réel une fois qu'il existe.

## Paramètres du crédit progressif

`coefficient_progression` (1,5), `montant_plancher` (50 000 FCFA), `plafond_produit`
(3 000 000 FCFA — le plafond que le système ne dépasse jamais, quel que soit le calcul),
`plafond_primo_emprunteur` (150 000 FCFA), et les constantes de modulation par le risque (1,3 / 2,0
/ 0,4 / 1,2). Même statut que la grille : point de départ ajustable par la coopérative, pas figé.
Détail de la formule et du rôle du modèle réel dans `docs/formules/`.

## nginx sans TLS

`infra/nginx/nginx.conf` écoute en clair sur le port 80 — usage LAN/démonstration de hackathon
assumé, pas un déploiement réel. Avant tout déploiement effectif : certificat TLS,
`listen 443 ssl`, redirection 80→443, en-tête `Strict-Transport-Security`. Pas construit
maintenant : temps non justifié pour un usage qui ne servira pas cette semaine.

## Ajustement du générateur CORE-SIM

`simulateur/simulateur/pipeline.py`, fonction `noms()` : à 12 000 sociétaires tirés sur 48
patronymes × 22 prénoms par sexe, deux sociétaires distincts (`societaire_id` différents,
donc pas un doublon technique) portaient presque certainement le même nom complet — gênant pour
un agent qui cherche par nom. Le nom complet est désormais garanti unique sur toute la population
générée (nouvelle tentative de tirage en cas de collision), sans suffixe numérique visible.

## Approximations de l'adaptateur CORE-SIM

Le générateur produit des données brutes mais pas d'échéancier de remboursement détaillé ni
certains champs de présentation. Ces valeurs sont **estimées, pas mesurées** :

- `capital_restant_du` : amortissement linéaire pour un crédit en cours ; montant intégral pour un
  crédit en souffrance (aucune donnée de remboursement partiel n'existe) ; zéro pour un crédit
  soldé.
- `statut` du sociétaire (actif/inactif/radié) : toujours "actif", le générateur ne modélise aucun
  churn.
- `nom_groupe` et `statut` du groupe : dérivés (nom depuis l'identifiant, statut depuis le taux de
  remboursement), le générateur ne produit ni l'un ni l'autre directement.
- `secteur` d'activité affiché au guichet : déduit du segment (agricole → agriculture, etc.), le
  générateur ne modélise pas de secteur d'activité distinct du segment.

## Simplifications d'architecture pour cette passe

- **Pas de feature store historisé, pas de batch.** Les features sont calculées à la demande à
  partir de CORE-SIM à chaque requête. Correct fonctionnellement, mais ne reflète pas encore la
  fraîcheur/staleness que la cascade est censée surveiller dans une vraie exploitation continue.
- **Recherche et dossier lisent CORE-SIM directement**, pas un index dédié pré-calculé. Suffisant
  au volume d'un hackathon, à revoir si la volumétrie ou la latence l'exigent.
- **Authentification : une seule session révocable de 8 heures** (stratégie base de données), pas
  un JWT court de 15 minutes séparé d'un renouvellement long. Choix délibéré pour la simplicité
  (moins de composants, plus facile à auditer) : la propriété qui compte — révocation côté serveur
  — est déjà pleinement assurée par ce choix unique.
- **Rétention du journal d'audit (`journal_audit`) : 1 an, purge automatique au-delà**
  (2026-08-07). Avant cette décision, rien n'était purgé : le journal grossissait indéfiniment,
  ce qui contredit le droit à l'effacement « quand la conservation n'est plus justifiée » de la
  loi togolaise n°2019-014 sur la protection des données personnelles — cette loi ne fixe pas de
  durée précise pour un journal de sécurité, d'où le choix de s'aligner sur le standard du
  secteur en l'absence de mandat plus précis : PCI-DSS, FISMA, HIPAA, SOX et GLBA convergent tous
  vers 1 an pour ce type de journal (avec au moins 90 jours immédiatement consultables). Implémenté
  dans `backend/solida/batch/jobs/purger_journal_audit.py`. **Non planifié automatiquement** :
  aucun ordonnanceur (cron, `pg_cron`) n'existe encore dans la pile SOLIDA — le script s'exécute
  manuellement ou via une tâche cron externe à ajouter à l'hôte avant un déploiement réel.
- **Fiche de justification : PDF généré côté serveur (WeasyPrint), archivage objet (SeaweedFS,
  pas MinIO).** `minio/minio` n'a plus reçu de nouvelle image Docker officielle depuis
  RELEASE.2025-09-07 (arrêt de la diffusion des binaires communautaires en octobre 2025) —
  épingler cette image aurait figé un composant jamais plus corrigé. SeaweedFS (`chrislusf/
  seaweedfs:4.40`, actif) expose la même API S3, lue par le même client Python `minio` (7.2.20) —
  aucun code applicatif ne dépend du nom "MinIO", seulement de l'API S3 qu'il expose. Seules les
  métadonnées (`fiche_archivee` : identifiant, chemin objet, auteur, horodatage) vivent dans
  `solida` ; le PDF lui-même reste dans le stockage objet, jamais en base.
- **`utilisateur.agence_id` porte le code `caisse_id` brut de CORE-SIM** ("CAI-00"), pas un
  libellé affichable ni une table `agence` séparée — nécessaire pour que le cloisonnement par
  agence du rôle `agent` compare des identifiants réels, mais la connexion affiche donc ce code
  brut plutôt qu'un nom de quartier. À corriger le jour où une vraie table de correspondance
  code → libellé existe (ni CORE-SIM ni le schéma `solida` n'en ont une aujourd'hui).
- **Cinq comptes de démonstration semés par migration** (`agent.be`, `agent.agoe`,
  `superviseur.reseau`, `auditeur.interne`, `administrateur.systeme`, mot de passe unique
  `solida-demo`). À supprimer avant tout déploiement réel — ce sont des comptes de hackathon, pas
  un provisioning de production.
- **Catalogue de produits, désormais réel** (2026-08-05, ferme le finding F4 de l'audit offensif) :
  `simulateur/pipeline.py` génère la table CORE-SIM `produits_credit` (5 lignes, une par segment
  existant — typologie confirmée par les pages produits publiques de FUCEC-Togo/RCPB/PAMECAS,
  réseaux de la confédération CIF-AO). `produit_id` est validé au scoring
  (`ScorerDemande._calculer`) : un identifiant inconnu lève `ProduitIntrouvable` (404). Aucune
  source officielle ne publiant de plafond/durée/taux précis par produit (donnée interne non
  publique à chaque réseau), les valeurs de `config/config.yaml` sont un point de départ calibré et
  ajustable — même statut que les autres paramètres de la grille, pas une vérité mesurée.
  Le plafond réellement **appliqué** par produit vit dans `grille_decision.seuils.plafonds_produits`
  (dict `produit_id → montant`), ajustable par la supervision depuis l'écran de paramétrage sans
  repasser par le générateur ; CORE-SIM reste la source des valeurs de référence initiales et de
  l'identité du catalogue (libellé, type de garantie, bornes de durée, taux). L'ancien
  `plafond_produit` scalaire unique a été retiré (migration `c1f8e5a3d947`).
  `credits` (table CORE-SIM déjà générée) porte aussi un `produit_id`, dérivé du `segment` déjà tiré
  par ligne — rétrofit choisi pour permettre l'affichage du produit dans l'historique de crédit du
  dossier sociétaire.
  Au passage, corrigé un bug préexistant du générateur découvert pendant ce travail : `max_remb`
  (capacité historique de remboursement, censée piloter la progression du plafond entre cycles dans
  `gen_credits`) était initialisé à `0.0` et jamais réassigné — le plafond de progression ne
  dépassait donc jamais `montant_median_primo` (100 000 FCFA), quel que soit le produit. Corrigé en
  l'alimentant depuis le montant des cycles déjà résolus (non `en_cours`) à `date_fin`.
- **Flux de scoring en deux temps** (`POST /previsualiser` puis `POST /confirmer`) : la
  prévisualisation ne persiste rien, la confirmation relit les mêmes tables CORE-SIM et recalcule
  à l'identique plutôt que de rejouer un résultat mis en cache — si les données CORE-SIM changent
  entre les deux appels (fenêtre de quelques secondes en pratique), le résultat confirmé peut
  différer marginalement de l'aperçu affiché. Accepté pour cette passe : pas de stockage
  intermédiaire d'un résultat non confirmé, ce qui aurait ajouté un état à gérer (expiration,
  nettoyage) pour un gain de cohérence négligeable à l'échelle d'une session de guichet.
- **`/registre` et `/parametrage/grille`** ont été câblés directement sur ces nouveaux endpoints
  (pas de contrat frontend préexistant à respecter, voir `06-cablage-frontend.md`) : leur forme
  (nommage `snake_case`, `{elements, total}`) reste une convention posée pour l'occasion, pas la
  reprise d'une spécification externe.

## Verrouillage de connexion : clé identifiant+IP (pentest round 3, finding 2)

Le compteur d'échecs (`LIMITE_ECHECS_CONNEXION = 5` / `FENETRE_VERROUILLAGE = 15 min`,
`routeurs/auth.py`) comptait uniquement par identifiant : n'importe qui connaissant un identifiant
valide pouvait verrouiller ce compte 15 minutes sans jamais avoir de mot de passe correct — DoS
anonyme ciblé, confirmé par le pentest round 3. Passé à une clé `identifiant:ip` (IP réelle,
restaurée derrière le tunnel Cloudflare via le module `realip` de nginx, cf. `infra/nginx/
nginx.conf`). Compromis assumé : un attaquant réparti sur plusieurs IP a désormais un compteur
distinct par IP, donc une protection légèrement affaiblie contre le brute-force distribué au
profit de la suppression du DoS anonyme mono-IP. CAPTCHA/preuve de travail écartés (nouvelle
dépendance non listée dans `pyproject.toml`, hors périmètre Règle Zéro).

## Immutabilité des paramètres scorecard via l'API (pentest round 3, finding 9)

`pdo`, `score_reference` et `odds_reference` n'étaient bornés que par `gt=0` côté schéma HTTP
(`schemas/grille.py`) — un appel API direct (hors UI) pouvait donc changer la mise à l'échelle
du score pour tout le réseau sans aucun garde-fou, alors que `03-MODELE/
10-politique-credit-decisions-en-attente.md` documente déjà que ces trois valeurs ne sont plus
éditables depuis l'écran Politique de crédit (transmises inchangées) tant que le modèle réel
n'est pas calibré. Plutôt qu'inventer une plage numérique non documentée (violerait la Règle
Zéro), le serveur impose désormais cette invariance déjà actée : toute tentative de changer ces
trois valeurs par rapport à la grille active est rejetée (`422 scorecard_immuable`). Se lève
automatiquement le jour où la calibration réelle (cf. section « Le modèle lui-même » ci-dessus)
est actée et qu'un vrai processus de recalibrage est défini.

## Auto-contrôle multi-octroi (pentest round 3, finding 12)

Le contrôle de sur-endettement (`societaire.a_credit_en_cours`) ne lit que CORE-SIM ; deux
décisions `confirmer` valides confirmées coup sur coup pour le même sociétaire passaient toutes
les deux, puisque CORE-SIM n'a par construction pas encore le temps de refléter la première.
Recherche faite (protocole §2, plusieurs sources croisées sur les systèmes d'origination de
crédit — LOS) : la dé-duplication contre les propres décisions internes du système (pas
seulement contre un bureau/système externe) est une pratique de base documentée des LOS,
justement à cause de ce délai. SOLIDA bloque donc désormais une nouvelle confirmation si une
décision `accord`/`accord_sous_condition` existe déjà pour ce sociétaire dans la fenêtre
`FENETRE_MULTI_OCTROI` (`scorer_demande.py`).

Fenêtre choisie : 8 heures, la durée de session déjà actée ailleurs (`DUREE_SESSION_SECONDES`,
`infrastructure/auth.py`) plutôt qu'un nouveau chiffre inventé pour l'occasion — au-delà d'une
session de guichet, CORE-SIM est censé avoir eu le temps de refléter un octroi confirmé. Cette
fenêtre est un point de départ technique, pas une vérité mesurée sur un vrai délai de
décaissement : à ajuster le jour où une intégration réelle avec le décaissement existe (SOLIDA
reste lecture seule sur CORE-SIM, aucun changement de ce côté).

## Blocage connu : `next build` (image `front` de production)

Depuis le 2026-08-05, `npm run build` (donc `docker compose build front`, cible `runner`) échoue de
façon reproductible lors du pré-rendu de pages internes à Next.js (`/`, `/_global-error`, jamais une
page applicative) avec `TypeError: Cannot read properties of null (reading 'useContext')` ou
`Cannot read properties of undefined (reading 'length')`, dans des frames "ignore-listed" (internes
à React/Next, pas notre code). Confirmé comme bug non résolu de Next.js 16 via le dépôt officiel
`vercel/next.js` (issues #84994, #86178, discussion #94667) — reproduit même sans `global-error.tsx`
personnalisé, et même avec (`frontend/app/global-error.tsx`, ajouté malgré tout par bonne pratique).
Testé et écarté : le contournement communautaire documenté (ci-dessus), `next build --webpack`
(donc pas spécifique à Turbopack), `reactStrictMode: false`. Aucune version plus récente ne corrige
ça à ce jour (dernière canary `16.3.1-canary.3` du jour même sans mention du correctif ; `16.3.0`,
notre version épinglée, est la dernière stable).

**Conséquence** : le conteneur `front` de production reste sur la dernière image construite avec
succès jusqu'à correction amont ou décision de contournement (ex. downgrade vers Next.js 15.x,
changement structurant hors périmètre d'une correction ponctuelle). `front-dev` (`next dev`, jamais
exposé en production) n'est pas affecté — c'est le canal de vérification en attendant. Décision
explicite de l'utilisateur (2026-08-05) : attendre plutôt que de downgrader dans l'urgence.
