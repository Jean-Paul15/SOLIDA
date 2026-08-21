# Graph Report - SOLIDA  (2026-08-21)

## Corpus Check
- 352 files · ~151,240 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1901 nodes · 3889 edges · 274 communities (111 shown, 163 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 233 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `75bcd10f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- adapters.py
- test_consulter_dossier_mapping.py
- test_scorecard.py
- test_scorer_demande_validations.py
- test_auth.py
- formatAmount
- Montant
- societaires/[id]/page.tsx
- test_scorer_demande.py
- contracts.ts
- cn
- routers/scoring.py
- RefreshFields.tsx
- SavingsMovements.tsx
- Monitoring sécurité — applicatif et infrastructure
- feature_store_core_sim.py
- test_scoring.py
- alert
- compilerOptions
- errors.py
- roles.ts
- command.tsx
- ParametresGrille
- dependencies
- test_lister_decisions.py
- GroupeCautionDialog.tsx
- parametrage.py
- devDependencies
- test_registre_et_grille.py
- Credit
- components.json
- test_scorer_demande_features.py
- CoreSimPostgresReader
- infrastructure/auth.py
- LecteurCoreSim
- Garantie
- NouvelleDemandeSheet.tsx
- ProduitCredit
- mappers/__init__.py
- FicheRepository
- PolitiqueCredit.tsx
- ProduitCredit
- values/decision.py
- orm_models/__init__.py
- demarrer.sh
- pipeline.py
- LoginForm.tsx
- Connection
- demarrer.ps1
- date
- useNewRequest.ts
- test_societaires.py
- MouvementEpargne
- AuditLog
- Utilisateur
- demande.py
- app/layout.tsx
- proxy.ts
- Engine
- EnTeteFiche
- SyntheseGroupe
- connexion/page.tsx
- ProduitCredit
- scripts
- SqlFicheArchiveeRepository
- comptes_demo.py
- package.json
- application_fastapi.py
- lint-staged
- .prettierrc.json
- _decomposition_to_schema
- pre-commit
- pre-push
- eslint.config.mjs
- commit-msg
- next.config.ts
- Any
- prettier
- typescript
- postcss.config.mjs
- coresim-init.sh
- solida-init.sh
- charger_postgres.py
- demo_recherche.py
- solida-backend
- routers/registre.py
- LireGrilleActive
- valider_mot_de_passe
- _inserer_evenement_test
- User
- Request
- lint-staged
- AsyncSession
- BaseModel
- DatabaseStrategy
- get
- post
- Request
- Response
- UUID
- get
- ConfigurationGrille
- get
- post
- get
- ProduitCredit
- get
- FicheJustification
- get
- post
- Response
- DossierSocietaire
- get
- Request
- FicheArchiveeRepository
- routers/auth.py
- GrilleRepository
- Response
- _ligne_to_decision
- ConfigurationGrille
- SeaweedfsFicheRepository
- ArchiverFiche
- GenererFiche
- LireDecision
- ListerProduits
- SqlAuditLog
- ResultatRechercheSocietaire
- Societaire
- RegistreDecisions.tsx
- Protocol
- ResultatRechercheSocietaire
- ._calculer
- ScorerDemande
- WeasyPrintFichePdfGenerator
- ConsulterDossier
- ListerSocietairesRecents
- RechercherSocietaire
- DossierSocietaire
- confirm
- env.py
- Utilisateur
- ModifierGrille
- Utilisateur
- Utilisateur
- ListerDecisions
- Utilisateur
- DecisionEnregistree
- .generer
- Utilisateur
- Utilisateur
- RecommendationPanel.tsx
- AccessToken
- ArchiverFiche
- AsyncSession
- Credit
- ResultatScoring
- test_consulter_dossier.py
- MembreGroupe
- MouvementEpargne
- MouvementEpargne
- ResultatRechercheSocietaire
- ConfigurationGrille
- LireGrilleActive
- ListerDecisions
- ListerProduits
- ListerSocietairesRecents
- ModifierGrille
- RechercherSocietaire
- WeasyPrintFichePdfGenerator
- fixture
- LecteurCoreSimPostgres
- DossierSocietaire
- ConfigurationGrille
- Credit
- MouvementEpargne
- LireGrilleActive
- ModifierGrille
- ListerProduits
- ListerDecisions
- ArchiverFiche
- GenererFiche
- TestClient
- ResultatScoring
- ResultatRechercheSocietaire
- ResultatRechercheSocietaire
- LireDecision
- DossierSocietaire
- ConfigurationGrille
- DecisionAEnregistrer
- DecisionRegistre
- DemandeScoring
- Engine
- EntreeScoring
- FicheJustification
- ResultatRechercheSocietaire
- ResultatScoring
- ScorerDemande
- ScorerDemande
- ConsulterDossier
- ListerSocietairesRecents
- RechercherSocietaire
- ConfigurationGrille
- User
- User
- User
- User
- User
- BaseModel
- CompteEpargne
- ConfigurationGrille
- ConsulterDossier
- Credit
- DatabaseStrategy
- date
- DecisionRegistreAffichee
- DossierSocietaire
- FeaturesIndividuelles
- GenererFiche
- get
- GroupeCaution
- LireDecision
- MembreGroupe
- MouvementEpargne
- NouvelleConfigurationGrille
- PageRegistre
- PointsVariable
- post
- ProbabiliteDefaut
- Request
- Response
- Societaire
- SqlAuditLog
- SqlDecisionRepository
- SqlGrilleRepository
- SyntheseGroupe
- User
- UserManager
- WeasyPrintFichePdfGenerator

## God Nodes (most connected - your core abstractions)
1. `cn()` - 101 edges
2. `User` - 39 edges
3. `LecteurCoreSim` - 32 edges
4. `Montant` - 32 edges
5. `_cas_usage()` - 31 edges
6. `CoreSimPostgresReader` - 28 edges
7. `ProbabiliteDefaut` - 27 edges
8. `AccesRefuse` - 24 edges
9. `formatAmount()` - 24 edges
10. `ProduitCredit` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_executer_compose_le_dossier_complet()` --calls--> `MouvementEpargne`  [EXTRACTED]
  backend/tests/application/test_consulter_dossier.py → frontend/lib/contracts.ts
- `_actualiser_features()` --calls--> `calculer_taux_endettement()`  [INFERRED]
  backend/solida/application/use_cases/scorer_demande_features.py → backend/solida/domain/rules/echeance.py
- `ListerProduits` --uses--> `ProduitCredit`  [INFERRED]
  backend/solida/application/use_cases/lister_produits.py → backend/solida/domain/entities/produit_credit.py
- `ListerProduits` --uses--> `LecteurCoreSim`  [INFERRED]
  backend/solida/application/use_cases/lister_produits.py → backend/solida/domain/ports/core_sim.py
- `ArchiverFiche` --uses--> `AccesRefuse`  [INFERRED]
  backend/solida/application/use_cases/archiver_fiche.py → backend/solida/domain/errors.py

## Import Cycles
- None detected.

## Communities (274 total, 163 thin omitted)

### Community 0 - "adapters.py"
Cohesion: 0.13
Nodes (22): ProduitCredit, BaseModel, ListerProduits, ProduitCredit, Fusionne l'identité du catalogue (CORE-SIM, référentiel) avec le plafond…, audit_log(), feature_store(), lecteur() (+14 more)

### Community 1 - "test_consulter_dossier_mapping.py"
Cohesion: 0.05
Nodes (57): Engine, PostgresEpargneReader, date, Engine, MouvementEpargne, PostgresGarantieReader, Engine, PostgresGroupeReader (+49 more)

### Community 2 - "test_scorecard.py"
Cohesion: 0.13
Nodes (20): calculer_score(), decomposer_en_points(), ParametresScorecard, PointsVariable, ProbabiliteDefaut, Mise à l'échelle probabilité de défaut -> score, par transformation PDO — voir…, Transforme une probabilité de défaut en score. Convention bancaire : score…, Répartit un log-odds en points de base et contributions par variable. Suppose… (+12 more)

### Community 3 - "test_scorer_demande_validations.py"
Cohesion: 0.11
Nodes (41): datetime, ProduitCredit, Societaire, valider_acces_agence(), valider_duree_dans_bornes(), valider_montant_sous_plafond(), valider_pas_de_credit_en_cours(), valider_pas_de_multi_octroi() (+33 more)

### Community 4 - "test_auth.py"
Cohesion: 0.07
Nodes (53): ArgumentParser, Dépendance FastAPI qui vérifie le rôle à l'endpoint. Ne remplace pas la…, require_role(), _main(), purge(), Purge du journal d'audit au-delà de sa durée de rétention. RÉTENTION : 1 an. La…, Supprime les entrées de `journal_audit` plus vieilles que `RETENTION`. Renvoie…, _build_parser() (+45 more)

### Community 5 - "formatAmount"
Cohesion: 0.17
Nodes (14): EconomicActivityPanel(), EconomicActivityPanelProps, LoanFields(), LoanSummary(), LoanSummaryProps, LIBELLE_NIVEAU_INSTRUCTION, ProfilePanel(), ProfilePanelProps (+6 more)

### Community 6 - "Montant"
Cohesion: 0.07
Nodes (42): ConstantScoringModel, Décomposition heuristique, PAS un modèle appris. `predire()` renvoie une…, Substitut du modèle réel : renvoie une probabilité de défaut fixe. Ce n'est pas…, Protocol, Retourne `(code_variable, contribution_log_odds)` pour chaque variable. Liste…, `ConstantScoringModel` (adapters/ml) est la seule implémentation existante pour…, ScoringModel, calculer_plafond() (+34 more)

### Community 7 - "societaires/[id]/page.tsx"
Cohesion: 0.22
Nodes (17): AppLayout(), PageGrille(), PageRegistre(), PageFiche(), PageFicheProps, PageResultatScoring(), PageResultatScoringProps, LIBELLE_SEGMENT (+9 more)

### Community 8 - "test_scorer_demande.py"
Cohesion: 0.09
Nodes (33): _AuditLogFactice, _cas_usage(), _configuration(), _DecisionRepositoryFactice, _demande(), _features_individuelles(), _features_solidaires(), _FeatureStoreFactice (+25 more)

### Community 9 - "contracts.ts"
Cohesion: 0.09
Nodes (21): ContributionsChart(), FactorsPanel(), FactorsPanelProps, ActualisationSituation, ApiErrorBody, CalculationMode, ContributionVariable, FamilleContribution (+13 more)

### Community 10 - "cn"
Cohesion: 0.09
Nodes (30): Preregl, ThresholdsTabProps, Alert(), AlertAction(), AlertDescription(), AlertTitle(), alertVariants, Avatar() (+22 more)

### Community 11 - "routers/scoring.py"
Cohesion: 0.12
Nodes (28): Implémente `FichePdfGenerator` : rend le même contenu que la fiche JSON/HTML du…, WeasyPrintFichePdfGenerator, ArchiverFiche, GenererFiche, DecisionEnregistree, EnTeteFiche, LireDecision, DecisionEnregistree (+20 more)

### Community 12 - "RefreshFields.tsx"
Cohesion: 0.17
Nodes (17): OBJETS, RefreshFieldsProps, PERIODES, RegistryFiltersProps, Input(), Label(), Select(), SelectContent() (+9 more)

### Community 13 - "SavingsMovements.tsx"
Cohesion: 0.21
Nodes (10): GuaranteePanel(), GuaranteePanelProps, FLECHE_TENDANCE, HORIZONS, SavingsMovements(), SyntheseEpargne, SyntheseGroupe, monthStart() (+2 more)

### Community 14 - "Monitoring sécurité — applicatif et infrastructure"
Cohesion: 0.25
Nodes (7): Ancrage réglementaire, Ce qui est explicitement laissé de côté (et pourquoi), Ce qui est surveillé aujourd'hui, Comptes bloqués — visibilité admin, Détection d'un volume de lecture hors norme, Intégrité du journal d'audit, Monitoring sécurité — applicatif et infrastructure

### Community 15 - "feature_store_core_sim.py"
Cohesion: 0.11
Nodes (19): FeatureStoreCoreSim, _max_jours_retard(), _montant_max_rembourse(), _nb_incidents_anterieurs(), date, Base historique de la progression : le plus gros montant déjà accordé, quel…, Calcule les features à la demande à partir de CORE-SIM — pas de feature store…, FeatureStore (+11 more)

### Community 16 - "test_scoring.py"
Cohesion: 0.17
Nodes (28): client_agent(), client_auditeur(), client_superviseur(), _demande(), fixture, TestClient, societaire_agence_agent(), societaire_autre_agence() (+20 more)

### Community 17 - "alert"
Cohesion: 0.24
Nodes (14): alert(), AlertedActor, detect(), _main(), datetime, Alerte sur un volume de lecture hors norme (recherche/dossier) par acteur. Ne…, Renvoie les acteurs ayant dépassé `SEUIL_LECTURES` lectures depuis `depuis`…, Détecte puis, sauf essai à blanc, journalise une entrée `alerte_volume_lecture`… (+6 more)

### Community 18 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 19 - "errors.py"
Cohesion: 0.16
Nodes (17): AccesRefuse, DomainError, DonneesInsuffisantes, DureeDemandeeInvalide, InvariantScoreViole, ModeleIndisponible, MontantDemandeInvalide, Les données disponibles ne permettent pas de calculer un score. (+9 more)

### Community 20 - "roles.ts"
Cohesion: 0.21
Nodes (9): ChangePasswordLayout(), Header(), HeaderProps, canAccessCreditPolicy(), canEditGrille(), canScore(), ROLES_MODIFICATION_GRILLE, ROLES_POLITIQUE_CREDIT (+1 more)

### Community 21 - "command.tsx"
Cohesion: 0.12
Nodes (12): RequestState, SocietaireSearch(), Command(), CommandDialog(), CommandEmpty(), CommandGroup(), CommandInput(), CommandItem() (+4 more)

### Community 22 - "ParametresGrille"
Cohesion: 0.12
Nodes (24): grille_to_schema(), NouvelleConfigurationGrille, ParametresGrille, ParametresProgressif, ParametresScorecard, BaseModel, Sans `date_activation` ni `active` : imposés par le dépôt, pas choisis par…, GrilleInvalide (+16 more)

### Community 23 - "dependencies"
Cohesion: 0.08
Nodes (25): class-variance-authority, clsx, cmdk, framer-motion, dependencies, class-variance-authority, clsx, cmdk (+17 more)

### Community 24 - "test_lister_decisions.py"
Cohesion: 0.29
Nodes (8): _decision(), _DecisionRepositoryFactice, _LecteurFactice, DecisionEnregistree, `DecisionRepository.lister` filtre par l'agence de l'AGENT (seule donnée…, _societaire(), test_decision_hors_agence_de_lagent_est_exclue_meme_si_le_depot_la_renvoie(), test_superviseur_sans_filtre_agence_voit_tout()

### Community 25 - "GroupeCautionDialog.tsx"
Cohesion: 0.09
Nodes (35): CreditHistoryTable(), CreditHistoryTableProps, DecisionsTableProps, FicheApercu(), FicheApercuProps, GroupeCautionDialogProps, LABEL_ROLE, LoanFieldsProps (+27 more)

### Community 26 - "parametrage.py"
Cohesion: 0.14
Nodes (20): ConfigurationGrille, _configuration_to_seuils(), _ligne_to_configuration(), Any, Engine, Implémente `GrilleRepository` contre `grille_decision` (schéma `solida`)., SqlGrilleRepository, LireGrilleActive (+12 more)

### Community 27 - "devDependencies"
Cohesion: 0.09
Nodes (23): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, husky, shadcn, tailwindcss (+15 more)

### Community 28 - "test_registre_et_grille.py"
Cohesion: 0.29
Nodes (14): _connecte(), _payload_grille(), TestClient, test_doublon_version_grille_renvoie_409_puis_une_version_unique_reussit(), test_lecture_grille_autorisee_a_lagent(), test_lecture_grille_autorisee_au_superviseur(), test_marge_hors_bornes_est_rejetee(), test_modification_grille_refusee_a_lagent() (+6 more)

### Community 29 - "Credit"
Cohesion: 0.22
Nodes (8): _capital_restant_du(), _ligne_to_credit(), PostgresCreditReader, Any, date, Engine, Approxime le capital restant dû. Le générateur produit des crédits bruts…, Credit

### Community 30 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 31 - "test_scorer_demande_features.py"
Cohesion: 0.20
Nodes (19): ActualisationSituation, _actualiser_features(), _features_to_dict(), DemandeScoring, FeaturesIndividuelles, Remplace les ratios qui dépendent du montant/de la durée demandés, ou d'un…, Ne garde que les champs numériques : `predire()`/`contributions()` attendent…, _revenu_effectif() (+11 more)

### Community 32 - "CoreSimPostgresReader"
Cohesion: 0.10
Nodes (18): CoreSimPostgresReader, CompteEpargne, date, Garantie, GroupeCaution, ProduitCredit, Societaire, SocietaireSearchResult (+10 more)

### Community 33 - "infrastructure/auth.py"
Cohesion: 0.15
Nodes (16): AccessTokenDatabase, current_active_user(), get_session(), get_strategy(), get_token_db(), get_user_db(), get_user_manager(), AsyncSession (+8 more)

### Community 34 - "LecteurCoreSim"
Cohesion: 0.06
Nodes (23): PostgresSocietaireReader, Engine, Societaire, SocietaireSearchResult, ListerSocietairesRecents, SocietaireSearchResult, Sociétés distinctes les plus récemment consultées par l'agent — construit à…, SocietaireSearchResult (+15 more)

### Community 36 - "NouvelleDemandeSheet.tsx"
Cohesion: 0.20
Nodes (12): NouvelleDemandeSheetProps, RefreshFields(), Button(), buttonVariants, Sheet(), SheetContent(), SheetDescription(), SheetFooter() (+4 more)

### Community 38 - "mappers/__init__.py"
Cohesion: 0.14
Nodes (24): fiche_to_schema(), DecisionEnregistree, EnTeteFiche, FicheJustification, Conversion des value objects du domaine vers les schémas pydantic exposés en…, decision_to_registre(), DecisionRegistreAffichee, decision_a_enregistrer_to_resultat_scoring() (+16 more)

### Community 39 - "FicheRepository"
Cohesion: 0.40
Nodes (3): FicheRepository, Protocol, Stockage objet des fiches PDF archivées — jamais en base (`solida` reste léger).

### Community 40 - "PolitiqueCredit.tsx"
Cohesion: 0.18
Nodes (13): Preregl, ProductsTab(), ProductsTabProps, Section(), SectionProps, SimulationTab(), SimulationTabProps, Tabs() (+5 more)

### Community 41 - "ProduitCredit"
Cohesion: 0.21
Nodes (8): PostgresProduitReader, Engine, ProduitCredit, Référentiel des produits de crédit — table CORE-SIM, pas les plafonds appliqués…, produit_to_schema(), ProduitCredit, ProduitCredit, Référentiel CORE-SIM : identité et valeurs de référence d'un produit de crédit.…

### Community 42 - "values/decision.py"
Cohesion: 0.07
Nodes (41): DecisionRepository, datetime, Protocol, Une décision `accord`/`accord_sous_condition` existe déjà pour ce sociétaire…, `decision_scoring` est en insertion seule : ce port n'expose donc aucune…, FichePdfGenerator, Protocol, ContexteCascade (+33 more)

### Community 43 - "orm_models/__init__.py"
Cohesion: 0.31
Nodes (10): AuditEvent, Base, DecisionScoring, FicheArchivee, Métadonnées seulement — le PDF lui-même vit dans le stockage objet (SeaweedFS),…, GrilleDecision, ModelVersion, datetime (+2 more)

### Community 44 - "demarrer.sh"
Cohesion: 0.32
Nodes (14): attendre_disponibilite(), banniere(), conclure(), configurer_env(), construire_images(), demarrer_services(), echouer(), etape() (+6 more)

### Community 45 - "pipeline.py"
Cohesion: 0.15
Nodes (8): choc_at(), gen_credits(), gen_epargne(), gen_membres(), noms(), SOLIDA -- Generateur CORE-SIM v3 (logique COOPEC / CIF). Modele reel des…, sigmoid(), z()

### Community 46 - "LoginForm.tsx"
Cohesion: 0.20
Nodes (12): LoginForm(), onSubmit(), InputGroup(), InputGroupAddon(), inputGroupAddonVariants, InputGroupButton(), inputGroupButtonVariants, InputGroupInput() (+4 more)

### Community 48 - "demarrer.ps1"
Cohesion: 0.30
Nodes (12): Build-Images(), Initialize-Donnees(), Invoke-Etape(), New-Secret(), Set-Configuration(), Show-Etape(), Show-Info(), Show-Ok() (+4 more)

### Community 50 - "useNewRequest.ts"
Cohesion: 0.07
Nodes (37): PagePrevisualisationScoring(), handleConfirm(), ChangePasswordForm(), onSubmit(), FicheActions(), handleArchive(), FicheActionsProps, GroupeCautionDialog() (+29 more)

### Community 51 - "test_societaires.py"
Cohesion: 0.24
Nodes (14): client_agent(), fixture, TestClient, societaire_agence_agent(), societaire_autre_agence(), test_dossier_dun_societaire_de_son_agence_est_accessible(), test_dossier_dun_societaire_dune_autre_agence_est_refuse(), test_dossier_introuvable_renvoie_404() (+6 more)

### Community 53 - "AuditLog"
Cohesion: 0.33
Nodes (3): AuditLog, Protocol, Chaque entrée : acteur, action, objet, horodatage. Jamais de mot de passe,…

### Community 56 - "app/layout.tsx"
Cohesion: 0.17
Nodes (12): ibmPlexMono, ibmPlexSans, sourceSerif4, metadata, Toaster(), TooltipProvider(), ScoringInput, ScoringResult (+4 more)

### Community 57 - "proxy.ts"
Cohesion: 0.40
Nodes (5): SESSION_COOKIE, config, proxy(), ROUTES_PROTEGEES, toLogin()

### Community 62 - "connexion/page.tsx"
Cohesion: 0.32
Nodes (4): LogoAnime(), CHEMINS, PARTICULES, SavingsFlowBeam()

### Community 64 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, start, test, typecheck

### Community 65 - "SqlFicheArchiveeRepository"
Cohesion: 0.33
Nodes (3): Engine, Implémente `FicheArchiveeRepository` contre `fiche_archivee` (schéma `solida`)., SqlFicheArchiveeRepository

### Community 68 - "package.json"
Cohesion: 0.33
Nodes (5): engines, node, name, private, version

### Community 69 - "application_fastapi.py"
Cohesion: 0.10
Nodes (18): client_ip_address(), Request, Dépendances FastAPI d'authentification exposées aux routers HTTP…, `X-Real-IP` : posé par nginx sur toute requête proxifiée vers l'API (seul point…, AccessLoggingMiddleware, Request, Response, Remplace le journal d'accès en texte brut d'uvicorn (désactivé via `--no-… (+10 more)

### Community 70 - "lint-staged"
Cohesion: 0.50
Nodes (5): lint-staged, *.{json,css,md}, *.{ts,tsx,js,jsx,mjs}, eslint --fix, prettier --write

### Community 71 - ".prettierrc.json"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 72 - "_decomposition_to_schema"
Cohesion: 0.23
Nodes (11): _Definition, explication(), famille(), formater_valeur(), libelle(), Traduction des codes de variables du modèle vers ce qu'un agent doit lire à…, sens(), _decomposition_to_schema() (+3 more)

### Community 121 - "routers/registre.py"
Cohesion: 0.27
Nodes (8): PageRegistre, BaseModel, ListerDecisions, DecisionRegistreAffichee, decision_repository(), lister_decisions(), lister(), get

### Community 123 - "valider_mot_de_passe"
Cohesion: 0.40
Nodes (9): MotDePasseInvalide, Le mot de passe proposé ne respecte pas la politique en vigueur., Lève `MotDePasseInvalide` si une règle est violée ; ne renvoie rien sinon.…, valider_mot_de_passe(), test_la_comparaison_a_la_liste_courante_ignore_la_casse(), test_un_mot_de_passe_conforme_ne_leve_rien(), test_un_mot_de_passe_courant_est_refuse(), test_un_mot_de_passe_trop_court_est_refuse() (+1 more)

### Community 124 - "_inserer_evenement_test"
Cohesion: 0.53
Nodes (5): _inserer_evenement_test(), Connection, UUID, test_solida_app_ne_peut_ni_modifier_ni_supprimer_journal_audit(), test_solida_purge_sans_le_flag_de_session_ne_peut_pas_supprimer()

### Community 125 - "User"
Cohesion: 0.20
Nodes (18): current_active_user(), Stub remplacé par `infrastructure.auth.current_active_user` à l'assemblage de…, User, ConsulterDossier, Équivalent de `authenticate()`, mais par `identifiant` plutôt que par e-mail.…, _agence_agent(), dossier(), groupe() (+10 more)

### Community 150 - "FicheArchiveeRepository"
Cohesion: 0.40
Nodes (3): FicheArchiveeRepository, Protocol, Métadonnées de l'archivage (le PDF lui-même est dans `FicheRepository`).

### Community 151 - "routers/auth.py"
Cohesion: 0.18
Nodes (22): AccessToken, load_common_passwords(), Détruit tous les jetons actifs d'un user — une seule session à la fois, et un…, revoke_user_tokens(), change_password(), ChangePasswordRequest, login(), LoginRequest (+14 more)

### Community 152 - "GrilleRepository"
Cohesion: 0.40
Nodes (4): GrilleRepository, ConfigurationGrille, Protocol, La grille est versionnée, jamais modifiée en place :…

### Community 154 - "_ligne_to_decision"
Cohesion: 0.19
Nodes (12): _decomposition_depuis_json(), _decomposition_to_json(), _ligne_to_decision(), Any, datetime, DecisionAEnregistrer, DecisionEnregistree, Engine (+4 more)

### Community 156 - "SeaweedfsFicheRepository"
Cohesion: 0.29
Nodes (4): Implémente `FicheRepository` contre la passerelle S3 de SeaweedFS — pas MinIO,…, SeaweedfsFicheRepository, _client_seaweedfs(), Minio

### Community 161 - "SqlAuditLog"
Cohesion: 0.22
Nodes (5): datetime, Engine, `objet` distincts les plus récemment journalisés pour cet acteur, du plus…, Implémente `AuditLog` contre `journal_audit` (schéma `solida`)., SqlAuditLog

### Community 165 - "RegistreDecisions.tsx"
Cohesion: 0.27
Nodes (7): DecisionsTable(), DecisionRegistreVue, RegistreDecisions(), RegistreDecisionsProps, RegistryFilters(), TOUS, useRegistryFilters()

### Community 168 - "._calculer"
Cohesion: 0.36
Nodes (6): DecisionAEnregistrer, DecisionEnregistree, DemandeScoring, Calcule le score sans l'enregistrer — l'agent doit encore confirm avant que…, Recalcule à l'identique (les features CORE-SIM peuvent avoir changé entre la…, ScorerDemande

### Community 175 - "confirm"
Cohesion: 0.48
Nodes (7): confirm(), _demande_depuis_entree(), preview(), DemandeScoring, post, ScoringResult, ScoringInput

### Community 176 - "env.py"
Cohesion: 0.83
Nodes (3): run_migrations_offline(), run_migrations_online(), url_migration()

### Community 187 - "RecommendationPanel.tsx"
Cohesion: 0.12
Nodes (26): NumberTicker(), PolitiqueCredit(), PolitiqueCreditProps, RecommendationPanel(), RecommendationPanelProps, ScoringResultView(), ScoringResultViewProps, ThresholdsTab() (+18 more)

### Community 195 - "test_consulter_dossier.py"
Cohesion: 0.20
Nodes (12): _credit(), _groupe(), _LecteurFactice, _membre(), CompteEpargne, date, GroupeCaution, _societaire() (+4 more)

## Knowledge Gaps
- **158 isolated node(s):** `Preregl`, `ThresholdsTabProps`, `RegistryFiltersProps`, `SavingsMonth`, `RegistreDecisionsProps` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **163 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConsulterDossier` connect `User` to `adapters.py`, `test_consulter_dossier_mapping.py`, `LecteurCoreSim`, `test_consulter_dossier.py`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `DossierSocietaire` connect `societaires/[id]/page.tsx` to `test_consulter_dossier_mapping.py`, `contracts.ts`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `test_executer_compose_le_dossier_complet()` connect `test_consulter_dossier.py` to `User`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `LecteurCoreSim` (e.g. with `FeatureStoreCoreSim` and `ConsulterDossier`) actually correct?**
  _`LecteurCoreSim` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Montant` (e.g. with `ParametresProgressif` and `SituationReexamen`) actually correct?**
  _`Montant` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `_cas_usage()` (e.g. with `ConfigurationGrille` and `ProduitCredit`) actually correct?**
  _`_cas_usage()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Preregl`, `ThresholdsTabProps`, `RegistryFiltersProps` to the rest of the system?**
  _158 weakly-connected nodes found - possible documentation gaps or missing edges._