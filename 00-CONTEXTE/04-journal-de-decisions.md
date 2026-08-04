# Journal des décisions d'architecture (ADR)

Chaque décision structurante est consignée ici. Format court et volontairement contraint.
Une décision absente de ce journal n'engage personne et peut être remise en cause sans préavis.

**Règle :** on n'annule pas une entrée, on en ajoute une nouvelle qui remplace la précédente
(statut `Remplacée par ADR-XXX`).

---

## ADR-001 — Séparation stricte CORE-SIM / SOLIDA

**Statut :** Acceptée
**Contexte :** Le système doit démontrer qu'il se branche sur un SI existant sans le modifier.
**Décision :** Deux bases PostgreSQL distinctes. SOLIDA accède à CORE-SIM en lecture seule via un
utilisateur dédié sans droit d'écriture, derrière un port d'accès unique.
**Conséquences :** Aucune jointure SQL entre les deux bases. Toute donnée nécessaire est copiée dans
SOLIDA par le batch. Coût : duplication assumée. Gain : la frontière est démontrable et le passage au
réel consiste à changer un seul adaptateur.

---

## ADR-002 — Explainable Boosting Machine comme modèle de socle

**Statut :** Acceptée
**Contexte :** Besoin d'un modèle interprétable, léger, capturant les non-linéarités.
**Décision :** EBM (`interpret` / InterpretML) en modèle principal ; régression logistique en
référence ; comparatif publié.
**Conséquences :** La structure additive permet une décomposition **exacte** du score en points par
variable, condition de la fiche de justification. Écarte les modèles d'ensemble par arbres, dont
l'attribution ne serait qu'approchée.

---

## ADR-003 — Graphe en relationnel + calcul en mémoire

**Statut :** Remplacée par ADR-016
**Contexte :** Besoin d'un graphe de caution sur ~25 000 nœuds.
**Décision :** Stockage des nœuds et arêtes en tables PostgreSQL classiques ; calcul des métriques
avec NetworkX en mémoire lors du batch ; résultats persistés dans le feature store.
**Alternatives écartées :** Neo4j (poids opérationnel, licence), Apache AGE (extension à compiler,
risque en 72 h).
**Conséquences :** À cette échelle, le graphe tient largement en mémoire. Aucune base
supplémentaire à exploiter. Si le volume dépassait le million de nœuds, cette décision serait à
revoir — ce n'est pas le cas d'une coopérative.

---

## ADR-004 — Architecture en cascade avec repli

**Statut :** Acceptée (langage mis à jour par ADR-016)
**Contexte :** Un sociétaire primo-emprunteur n'a pas d'historique de crédit, et l'immense majorité
du portefeuille n'appartient à aucun groupe de caution.
**Décision :** Socle individuel toujours actif (épargne, remboursement) ; enrichissement par la
couche solidaire conditionnel au segment de groupe ; repli sur le socle seul avec application du
crédit progressif.
**Conséquences :** Deux modèles à entraîner et à versionner, pas un. Le système reste opérationnel
sur le cas le plus fréquent en microfinance — un crédit individuel sans groupe.

---

## ADR-005 — PostgreSQL nu plutôt que Supabase

**Statut :** Acceptée
**Contexte :** Choix de la couche de persistance et d'authentification.
**Décision :** PostgreSQL 16 auto-hébergé. Authentification assurée par le backend FastAPI.
**Alternatives écartées :** Supabase auto-hébergé (empile Kong, GoTrue, Realtime, Storage, PostgREST
pour des fonctions dont nous n'utiliserions qu'une fraction — contraire à l'argument de légèreté
que nous défendons devant le jury) ; Supabase géré (données hors du périmètre de la coopérative,
contraire à l'argument de souveraineté).
**Conséquences :** Un peu plus de code d'authentification à écrire. En contrepartie, la démonstration
« ça tourne sur un serveur modeste dans l'agence » reste vraie.

---

## ADR-006 — MinIO pour le stockage objet

**Statut :** Acceptée
**Décision :** MinIO auto-hébergé, compatible S3, pour trois usages : artefacts MLflow, fiches de
justification PDF archivées, instantanés de données.
**Conséquences :** Une API S3 unique côté code. Migration vers S3 réel possible sans changer le code.

---

## ADR-007 — Le score est un entier, pas une probabilité affichée

**Statut :** Acceptée
**Contexte :** Sur données synthétiques, annoncer « 4,2 % de risque de défaut » est indéfendable.
**Décision :** L'interface affiche un score entier et une tranche. La probabilité brute est
conservée en base pour l'audit et le recalibrage, mais n'est jamais présentée comme une prédiction
absolue tant que le modèle n'a pas été recalibré sur données réelles.
**Conséquences :** Discours cohérent devant un jury sectoriel : SOLIDA classe et segmente, il ne
prédit pas un taux absolu.

---

## ADR-008 — Français comme langue unique

**Statut :** Acceptée
**Décision :** Interface, messages d'erreur, documentation et vocabulaire de domaine en français.
Le code technique (noms de classes d'infrastructure, librairies) reste en anglais.
**Conséquences :** Pas d'internationalisation. Le vocabulaire du glossaire est normatif.

---

## ADR-009 — FastAPI-Users pour l'authentification

**Statut :** Acceptée (remplace la partie « auth maison » sous-entendue par ADR-005)
**Contexte :** Il ne faut pas écrire d'auth from scratch, mais pas non plus ajouter un service d'IAM
lourd. Débat récurrent sur Supabase.
**Décision :** FastAPI-Users (librairie Python, licence MIT), embarquée dans le backend. Elle
fournit gestion d'utilisateurs, hachage Argon2, sessions cookie/JWT, révocation. On y ajoute nos
rôles et le cloisonnement par agence.
**Alternatives écartées :** Supabase (le RLS ne rend rien derrière un backend FastAPI, 7 services
pour en exploiter 2) ; Zitadel / Authentik / Keycloak (vrais IAM surdimensionnés pour 4 rôles) ;
auth maison (inutile et risqué).
**Conséquences :** Auth maintenue sans service supplémentaire, audit co-localisé avec les décisions.
Évolution possible vers Zitadel (OIDC, Go) si une IMF demande du SSO, sans réécrire les rôles.

---

## ADR-010 — Un seul backend, en Python

**Statut :** Acceptée
**Contexte :** Tentation d'ajouter un service Go à côté de FastAPI.
**Décision :** Un seul backend FastAPI (Python) pour le domaine, le ML et l'API. Pas de service Go
écrit par l'équipe.
**Alternatives écartées :** microservice Go maison (deux langages pour 4 personnes en 72 h, gain
nul). Le seul Go acceptable serait un outil préfabriqué qu'on n'écrit pas (ex. Zitadel), non retenu
pour l'instant.
**Conséquences :** Une seule stack backend, un seul environnement, moins de couplage. Cohérent avec
« éviter le sur-engineering ».

---

## ADR-011 — DVC pour le versionnage des données et des modèles

**Statut :** Acceptée
**Contexte :** Besoin de rejouer une décision à l'identique, donc de versionner données et modèles.
**Décision :** DVC (Apache 2.0), avec MinIO comme remote, complémentaire de MLflow (DVC pour données
et artefacts, MLflow pour expériences et registre).
**Alternatives écartées :** lakeFS (échelle data lake, surdimensionné) ; Git LFS (pas de lignage ni
de pipeline) ; rien (aucune reproductibilité).
**Conséquences :** Reproductibilité complète et démontrable. Un remote MinIO mutualisé pour DVC,
MLflow et les fiches.

---

## ADR-012 — Gouvernance comme du code, pas de catalogue

**Statut :** Acceptée
**Contexte :** Besoin d'une gouvernance de données automatique.
**Décision :** Gouvernance intégrée au système sous forme de règles et de jobs (lignage, rétention,
classification PII, matrice d'accès, qualité par Pandera). Pas d'outil de catalogue.
**Alternatives écartées :** OpenMetadata, DataHub, Amundsen (services lourds à exploiter, contraires
à la légèreté).
**Conséquences :** La gouvernance se démontre par des artefacts du système lui-même (registre,
matrice d'accès, rapports), sans plateforme supplémentaire.

---

## ADR-013 — Intégration ancrée sur le Système Unique d'Information de la CIF

**Statut :** Acceptée
**Contexte :** La CIF a déployé dès 2020 un Système Unique d'Information (SIG) connectant ses six
faîtières, plutôt que six systèmes hétérogènes.
**Décision :** Positionner le contrat d'intégration en priorité comme un branchement sur ce SIG
partagé, tout en gardant les trois modes d'intégration génériques pour les cas hors SIG.
**Conséquences :** Argument de déployabilité renforcé (« on se branche sur votre système unique
existant »). La démonstration s'ancre sur une coopérative de type FUCEC-TOGO.

---

## ADR-014 — Conditions micro-économiques sectorielles, captées en interne et de façon adaptative

**Statut :** Acceptée
**Contexte :** Le risque agricole (dérèglement climatique, saisons devenues irrégulières) est le
premier moteur de défaut en Afrique de l'Ouest. Mais l'irrégularité croissante des saisons rend une
variable de calendrier agricole fixe fragile et trompeuse : le début de la saison des pluies varie
de plusieurs semaines d'une année à l'autre et se décale.
**Décision :** Ne pas encoder de saisonnalité calendaire fixe, ni intégrer de données climatiques
externes. Capter la santé micro-économique de **chaque secteur** de façon **adaptative**, à partir
du seul portefeuille de l'IMF, sur fenêtre glissante : tendance d'impayés du secteur, vélocité de
remboursement, dynamique d'épargne, accélération. Le système observe l'état réel du secteur au lieu
de supposer quand la saison devrait avoir lieu.
**Alternatives écartées :** saisonnalité calendaire fixe (suppose une régularité qui disparaît) ;
données climatiques externes, pluviométrie, NDVI, CLIMADA / OS-Climate (contre souveraineté et
légèreté ; conçues pour de grandes institutions, pas pour des IMF à faible connectivité).
**Conséquences :** Signal capté sans dépendance externe ni hypothèse de calendrier. Générateur : un
choc sectoriel latent variable dans le temps remplace toute logique de calendrier. Risque de
procyclicité borné (poids limité, action sur le montant plutôt que refus, surveillance du taux
d'approbation par secteur). Priorité P1/P2, jamais P0. À valider avec les experts métier le jour J.

---

## ADR-015 — Seuil de décision fixé par matrice de coûts

**Statut :** Acceptée
**Contexte :** Sur données déséquilibrées, un seuil de 0,50 est absurde ; le bon seuil dépend du
coût réel des erreurs (perte en capital contre marge manquée).
**Décision :** Fixer la borne accord/refus de la grille par la minimisation du coût espéré,
seuil* = C_FP / (C_FP + C_FN), avec C_FN = LGD réaliste (60-80 %, pas 100 %) × exposition et
C_FP = marge nette perdue. Le seuil en probabilité se traduit en score via la formule PDO et
alimente la grille existante. Version aboutie : décider sur la perte espérée (PD × LGD × exposition).
**Conséquences :** Argument d'impact financier chiffré en FCFA. Prérequis : calibration honnête.
Garde-fous : décision humaine, surveillance par segment, recalcul si les coûts changent. Pas un
mécanisme séparé : c'est la façon économiquement fondée de fixer la grille.

---

## Modèle pour une nouvelle entrée

```
## ADR-016 — Épargne et remboursement en socle, couche solidaire en segment, sans mesures de graphe

**Statut :** Acceptée. Remplace ADR-003.
**Contexte :** ADR-003 dimensionnait un graphe de caution de ~25 000 nœuds, avec centralité
(betweenness) et propagation de réputation. Vérification faite : la CIF est un réseau de
**coopératives d'épargne et de crédit** (COOPEC), pas un dispositif de crédit de groupe dense. Le
crédit est majoritairement **individuel, adossé à l'épargne nantie** ; le bilan social FUCEC-TOGO
rapporte 70 646 emprunteurs pour 287 643 sociétaires, soit ~25 % de membres emprunteurs, et le crédit
de groupe (groupements de femmes) est un segment minoritaire. La densité de réseau qu'exigent des
métriques de centralité n'existe pas dans un portefeuille de crédit individuel dominant.
**Décision :** le socle du score porte sur l'épargne (régularité, tendance, ancienneté de la
relation, ratio à l'épargne nantie) et le comportement de remboursement, disponibles pour 100 % du
portefeuille dès la première demande. Une **couche solidaire simple** (taux de remboursement du
groupe hors soi, taille, « déjà secouru ») s'active uniquement sur le segment des crédits de groupe.
Aucune mesure de centralité (betweenness, PageRank) ni propagation de réputation.
**Conséquences :** le graphe de caution (`01-ARCHITECTURE/07`, ex-« Stratégie graphe ») devient
« Stratégie de la couche solidaire ». Les variables `degre_garant`, `degre_beneficiaire`,
`taux_defaut_voisinage`, `centralite_intermediarite`, `score_reputation_propage` sont retirées du
catalogue de variables. L'écran E5 devient un écran de groupe de caution (liste), pas une
visualisation de réseau à plusieurs degrés.

---

## ADR-017 — Note qualitative de l'agent : champ optionnel, désactivé par défaut

**Statut :** Acceptée
**Contexte :** L'information « soft » de l'agent de crédit (appréciation de terrain) est documentée
comme prédictive dans la littérature, mais elle est rarement un champ structuré dans un système de
gestion de microfinance — elle vit en texte libre ou n'est simplement pas saisie. Nous ne savons pas
si elle existe sous forme exploitable dans le SI des coopératives CIF.
**Décision :** le champ `note_agent` existe dans le schéma comme option, **désactivé par défaut**
dans le générateur et absent du jeu de variables du modèle présenté au jury. Il n'est activé que si
un praticien confirme sa saisie structurée.
**Conséquences :** le score ne dépend d'aucune donnée dont l'existence n'est pas vérifiée. C'est un
choix plus modeste en performance affichée, mais defendable devant un expert métier.

---

## ADR-018 — Dépôt unique versionnant SOLIDA-FOUNDATION

**Statut :** Acceptée. Remplace la stratégie multi-dépôts de `09-DEVOPS/01-git-workflow.md`.
**Contexte :** `09-DEVOPS/01` décidait quatre dépôts séparés (`solida-backend`, `solida-frontend`,
`solida-simulateur`, `solida-infra`) et l'exclusion pure et simple de `SOLIDA-FOUNDATION/`,
`AGENTS.md`, `CLAUDE.md` du contrôle de version, diffusés hors Git. Avec une équipe réduite et le
besoin de démarrer vite le socle frontend, la coordination inter-dépôts coûte plus qu'elle ne
protège, et la diffusion hors Git du dossier de principes crée un risque de dérive documenté par le
fichier lui-même (« deux personnes travailleront avec deux versions différentes des règles »).
**Décision :** un dépôt unique `SOLIDA` (`github.com/Jean-Paul15/SOLIDA`), organisé en dossiers
(`00-CONTEXTE/` … `10-PLAN-HACKATHON/` pour les principes, `frontend/`, puis `backend/`, `infra/`,
`simulateur/` au fur et à mesure) plutôt qu'en dépôts séparés. `SOLIDA-FOUNDATION` est versionné et
poussé avec le code, sans exclusion `.gitignore`.
**Alternatives écartées :** monorepo avec sous-modules Git (complexité d'outillage disproportionnée
pour 72 h) ; conserver 4 dépôts avec le dossier de principes en dépôt privé séparé (solution
documentée initialement, écartée par choix explicite de l'équipe pour la vitesse).
**Conséquences :** le dossier de principes est désormais public dans l'historique Git du dépôt de
code — s'il devait redevenir confidentiel, il faudrait purger l'historique, coût assumé. Le
cloisonnement par dossier remplace le cloisonnement par dépôt : la règle « une branche courte par
module » de `09-DEVOPS/01` continue de s'appliquer à l'intérieur du dépôt unique.

---

## ADR-0XX — Titre court

**Statut :** Proposée | Acceptée | Remplacée par ADR-0YY
**Contexte :** Le problème à trancher, en deux phrases.
**Décision :** Ce qui est décidé, à l'impératif.
**Alternatives écartées :** Lesquelles, et pourquoi.
**Conséquences :** Ce que cela coûte et ce que cela apporte.
```
