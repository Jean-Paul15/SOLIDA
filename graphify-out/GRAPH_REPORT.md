# Graph Report - SOLIDA  (2026-09-14)

## Corpus Check
- 493 files · ~202,088 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3049 nodes · 6928 edges · 214 communities (187 shown, 27 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 396 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c17398f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- demande-context.tsx
- test_consulter_dossier_mapping.py
- test_scorecard.py
- test_scorer_demande_validations.py
- solida_engine
- values/decision.py
- NouvelleDemandeSheet.tsx
- societaires/[id]/page.tsx
- test_scorer_demande.py
- frontend/lib/contracts.ts
- cn
- CalibrateurPlatt
- CentreNotificationsSuperviseur.tsx
- solida_modelisation/features.py
- Monitoring sécurité — applicatif et infrastructure
- values/features.py
- test_scoring.py
- mlflow_tracking.py
- compilerOptions
- CoreSimReader
- parametrage.py
- routers/notifications.py
- TrancheDecision
- dependencies
- test_lister_decisions.py
- CentreNotificationsAgent.tsx
- Montant
- ModeleSocle
- test_registre_et_grille.py
- Connectivité faible et connecteur de données réel
- components.json
- dependencies.py
- CoreSimPostgresReader
- adapters.py
- DecisionAEnregistrer
- entrainement.py
- Étapes
- ProbabiliteDefaut
- mappers/__init__.py
- De la probabilité au score, et du score à la décision
- calculer_features_groupe
- authenticate_societaire.py
- ModeCalcul
- Composants tiers et logiciels libres
- demarrer.sh
- pipeline.py
- compilerOptions
- ScoringResult
- demarrer.ps1
- Évaluation
- frontend/lib/services/error-service.ts
- test_societaires.py
- Décisions provisoires à revoir
- UtilisateurResume
- _decomposition_to_schema
- scorer_demande.py
- frontend-societaire/components.json
- Formule cible du crédit progressif — à activer quand le modèle EBM réel existe
- Sélection de variables et prétraitement — principes
- core_sim_postgres_reader.py
- errors.py
- feature_store_core_sim.py
- connexion/page.tsx
- MLflow
- scripts
- dependencies
- metrics.py
- ScoringModel
- frontend/package.json
- Éthique de la décision automatisée
- DVC — versionnage des données et des modèles
- .prettierrc.json
- Protocole obligatoire pour les agents (Claude Code, Codex)
- pre-commit
- pre-push
- eslint.config.mjs
- commit-msg
- next.config.ts
- test_notifications.py
- Protocole obligatoire pour les agents (Claude Code, Codex)
- postcss.config.mjs
- coresim-init.sh
- solida-init.sh
- charger_postgres.py
- demo_recherche.py
- DonneesGroupeBrutes
- solida-backend
- postgres_credit_reader.py
- Feature engineering
- AccessLoggingMiddleware
- _inserer_evenement_test
- Cascade et démarrage à froid
- Leçons du prototype simulateur (retiré)
- Détection de dérive
- Cas d'usage et routeurs HTTP
- Transmission complète — SOLIDA
- Contrats et implémentations factices
- Docker et développement
- equite.py
- Principes de modélisation
- Cycle de vie du modèle
- Monitoring et mise en production
- SOLIDA
- Politique de crédit — décisions en attente
- Câblage frontend → backend réel
- continuite/README.md
- Sécurité — mesures appliquées
- Postgres et simulateur CORE-SIM
- modelisation/README.md
- Model card — SOCLE EBM
- montant_maximal_supportable
- SOLIDA -- Generateur CORE-SIM v4
- Rôles applicatifs vs organigramme réel (CEF-MF Lomé)
- scripts
- Persistance et migrations
- Journal de discussion conservé pour reprise
- Hooks Git et CI
- orm_models/__init__.py
- test_lister_notifications.py
- Scaffold backend et outillage Python
- Adaptateur CORE-SIM
- Constat Claude — plafonds par produit
- Design system — implémentation
- Calcul de l'échéance mensuelle
- Décisions techniques SOCLE
- Modélisation SOCLE SOLIDA
- echeance.py
- SOLIDA — le crédit qui se justifie, pas qui se subit
- Écrans livrés
- devDependencies
- shadcn
- 06-outils.md
- frontend/README.md
- valider_mot_de_passe
- data/README.md
- Authentification
- AccesRefuse
- proxy.ts
- onSubmit
- Convention de nommage technique (refactor SOLID / anglicisation)
- Societaire
- test_features.py
- test_consulter_dossier.py
- archiver_fiche.py
- .__init__
- SoldeMensuelEpargne
- eslint-config-next
- routers/registre.py
- DemandeSocietaire
- ArchiverNotification
- mesurer_apport_couche_solidaire
- RecommendationPanel.tsx
- grille_repository_sql.py
- post-commit
- frontend/app/layout.tsx
- Model card — modèle enrichi (couche solidaire)
- cli.py
- frontend-societaire/package.json
- husky
- @types/node
- construire_cible
- devDependencies
- @types/react
- GrilleRepository
- routers/scoring.py
- Interroger plusieurs bases hétérogènes en lecture seule (MySQL / Postgres / Oracle)
- _FakeScoringModel
- User
- post-checkout
- routers/auth.py
- routers/portail.py
- frontend-societaire/eslint.config.mjs
- frontend-societaire/next.config.ts
- frontend-societaire/postcss.config.mjs

## God Nodes (most connected - your core abstractions)
1. `cn()` - 101 edges
2. `Montant` - 62 edges
3. `User` - 46 edges
4. `CoreSimReader` - 46 edges
5. `ProbabiliteDefaut` - 46 edges
6. `CoreSimPostgresReader` - 42 edges
7. `AccesRefuse` - 39 edges
8. `_build_use_case()` - 39 edges
9. `Societaire` - 38 edges
10. `DemandeSocietaire` - 36 edges

## Surprising Connections (you probably didn't know these)
- `CoreSimPostgresReader` --uses--> `SoldeMensuelEpargne`  [INFERRED]
  backend/solida/adapters/core_sim/core_sim_postgres_reader.py → modelisation/src/solida_modelisation/features_epargne.py
- `PostgresDonneesGroupeReader` --uses--> `AppartenanceGie`  [INFERRED]
  backend/solida/adapters/core_sim/postgres_donnees_groupe_reader.py → modelisation/src/solida_modelisation/features_groupe.py
- `PostgresDonneesGroupeReader` --uses--> `CreditGroupeAnterieur`  [INFERRED]
  backend/solida/adapters/core_sim/postgres_donnees_groupe_reader.py → modelisation/src/solida_modelisation/features_groupe.py
- `PostgresSoldeMensuelReader` --uses--> `SoldeMensuelEpargne`  [INFERRED]
  backend/solida/adapters/core_sim/postgres_solde_mensuel_reader.py → modelisation/src/solida_modelisation/features_epargne.py
- `CoreSimReader` --uses--> `SoldeMensuelEpargne`  [INFERRED]
  backend/solida/domain/ports/core_sim.py → modelisation/src/solida_modelisation/features_epargne.py

## Import Cycles
- None detected.

## Communities (214 total, 27 thin omitted)

### Community 0 - "demande-context.tsx"
Cohesion: 0.05
Nodes (62): BonjourPage(), ConfirmationPage(), DureePage(), DUREES_STANDARD, ibmPlexMono, ibmPlexSans, sourceSerif4, metadata (+54 more)

### Community 1 - "test_consulter_dossier_mapping.py"
Cohesion: 0.07
Nodes (51): dossier_to_schema(), groupe_to_schema(), DossierSocietaire, SyntheseGroupe, CreditResume, BaseModel, DossierSocietaire, BaseModel (+43 more)

### Community 2 - "test_scorecard.py"
Cohesion: 0.20
Nodes (19): InvariantScoreViole, La décomposition en points ne somme pas au score : le scoring est rejeté., calculer_score(), decomposer_en_points(), Transforme une probabilité de défaut en score. Convention bancaire : score…, Répartit un log-odds en points de base et contributions par variable. Suppose…, Lève InvariantScoreViole si la décomposition ne somme pas au score rendu. Une…, verifier_invariant_decomposition() (+11 more)

### Community 3 - "test_scorer_demande_validations.py"
Cohesion: 0.11
Nodes (37): datetime, ProduitCredit, valider_acces_agence(), valider_duree_dans_bornes(), valider_montant_sous_plafond_institutionnel(), valider_pas_de_credit_en_cours(), valider_pas_de_multi_octroi(), valider_produit_catalogue() (+29 more)

### Community 4 - "solida_engine"
Cohesion: 0.05
Nodes (67): ArgumentParser, alert(), AlertedActor, detect(), _main(), datetime, Alerte les pics de lecture sans bloquer automatiquement les comptes. Le seuil…, Renvoie les acteurs au-dessus du seuil, sans écrire. (+59 more)

### Community 5 - "values/decision.py"
Cohesion: 0.12
Nodes (16): fiche_to_schema(), FicheJustification, Implémente `FichePdfGenerator` : rend le même contenu que la fiche JSON/HTML du…, WeasyPrintFichePdfGenerator, LireDecision, DecisionRepository, datetime, Protocol (+8 more)

### Community 6 - "NouvelleDemandeSheet.tsx"
Cohesion: 0.08
Nodes (31): CreditHistoryTable(), EconomicActivityPanelProps, LoanFieldsProps, NouvelleDemandeSheet(), NouvelleDemandeSheetProps, RefreshFields(), DUREES_STANDARD, useNewRequest() (+23 more)

### Community 7 - "societaires/[id]/page.tsx"
Cohesion: 0.12
Nodes (29): AppLayout(), PageNotifications(), PageGrille(), PageRegistre(), PageFiche(), PageFicheProps, PageResultatScoring(), PageResultatScoringProps (+21 more)

### Community 8 - "test_scorer_demande.py"
Cohesion: 0.12
Nodes (33): _build_use_case(), _configuration(), _demande(), _donnees_groupe_eligibles(), _FakeAuditLog, _FakeCoreSimReader, _FakeDecisionRepository, _FakeGrilleRepository (+25 more)

### Community 9 - "frontend/lib/contracts.ts"
Cohesion: 0.06
Nodes (36): ConditionsReexamen(), ConditionsReexamenProps, ContributionsChart(), FactorsPanel(), FicheApercu(), FicheApercuProps, GroupeCautionDialog(), handleOpenChange() (+28 more)

### Community 10 - "cn"
Cohesion: 0.06
Nodes (55): GroupeCautionDialogProps, GroupMembersTable(), RequestState, Avatar(), AvatarBadge(), AvatarFallback(), AvatarGroup(), AvatarGroupCount() (+47 more)

### Community 11 - "CalibrateurPlatt"
Cohesion: 0.11
Nodes (33): charger_bundle(), _distributions_reference(), empreinte_fichier(), ManifesteModele, Any, DataFrame, Path, Bundle versionné et vérifié du modèle SOCLE. (+25 more)

### Community 12 - "CentreNotificationsSuperviseur.tsx"
Cohesion: 0.11
Nodes (27): EconomicActivityPanel(), LoanFields(), LoanSummary(), LoanSummaryProps, LIBELLE_NIVEAU_INSTRUCTION, ProfilePanel(), ProfilePanelProps, OBJETS (+19 more)

### Community 13 - "solida_modelisation/features.py"
Cohesion: 0.13
Nodes (32): _construire_jeu(), construire_jeu_enrichi(), construire_jeu_socle(), ecrire_jeu_enrichi(), ecrire_jeu_socle(), _features_epargne(), _historique_observable(), lire_tables_brutes() (+24 more)

### Community 14 - "Monitoring sécurité — applicatif et infrastructure"
Cohesion: 0.25
Nodes (7): Ancrage réglementaire, Ce qui est explicitement laissé de côté (et pourquoi), Ce qui est surveillé aujourd'hui, Comptes bloqués — visibilité admin, Détection d'un volume de lecture hors norme, Intégrité du journal d'audit, Monitoring sécurité — applicatif et infrastructure

### Community 15 - "values/features.py"
Cohesion: 0.21
Nodes (10): FeatureStore, date, Protocol, `None` si `gie_id` ne correspond à aucun groupe connu — jamais appelé pour une…, Simplification assumée pour cette passe, sans pipeline batch : `ecrire_lot`…, FeaturesIndividuelles, FeaturesSolidaires, Couche solidaire : historique du groupe emprunteur lui-même (arbitrage… (+2 more)

### Community 16 - "test_scoring.py"
Cohesion: 0.16
Nodes (30): client_agent(), client_auditeur(), client_superviseur(), _demande(), fixture, TestClient, Le message doit rester exploitable par l'agent (pas de jargon technique), et le…, societaire_agence_agent() (+22 more)

### Community 17 - "mlflow_tracking.py"
Cohesion: 0.31
Nodes (13): actif(), _dependances_mlflow(), _journaliser_ebm(), journaliser_enrichi(), _journaliser_metriques(), journaliser_reference(), journaliser_socle(), Any (+5 more)

### Community 18 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 19 - "CoreSimReader"
Cohesion: 0.11
Nodes (12): CoreSimReader, date, ProduitCredit, Protocol, SocietaireSearchResult, Accès en lecture seule à CORE-SIM. Aucune implémentation de ce port n'écrit…, `agence_id` restreint la recherche à une agence : cloisonnement du rôle…, Nombre réel de correspondances pour `terme` (même prédicat que… (+4 more)

### Community 20 - "parametrage.py"
Cohesion: 0.14
Nodes (22): grille_to_schema(), ConfigurationGrille, ConfigurationGrille, NouvelleConfigurationGrille, ParametresGrille, ParametresProgressif, ParametresScorecard, BaseModel (+14 more)

### Community 21 - "routers/notifications.py"
Cohesion: 0.17
Nodes (21): AgentAgence, AssignerNotificationRequest, DemandeSocietaireNotification, PageNotifications, BaseModel, ListerNotifications, demande_societaire_repository(), utilisateur_repository() (+13 more)

### Community 22 - "TrancheDecision"
Cohesion: 0.16
Nodes (19): GrilleInvalide, Les paramètres de la grille de décision sont incohérents., decider(), ParametresGrille, Seuils de la grille, fondés sur la matrice de coûts — voir docs/formules/., Détermine la tranche à partir du seuil économique marge / (marge + LGD). Le…, StrEnum, Tranche de la grille de décision. Valeurs alignées sur le contrat frontend. Le… (+11 more)

### Community 23 - "dependencies"
Cohesion: 0.08
Nodes (25): cmdk, framer-motion, dependencies, class-variance-authority, clsx, cmdk, framer-motion, lucide-react (+17 more)

### Community 24 - "test_lister_decisions.py"
Cohesion: 0.31
Nodes (7): _decision(), _FakeCoreSimReader, _FakeDecisionRepository, `DecisionRepository.lister` filtre par l'agence de l'AGENT (seule donnée…, _societaire(), test_decision_hors_agence_de_lagent_est_exclue_meme_si_le_depot_la_renvoie(), test_superviseur_sans_filtre_agence_voit_tout()

### Community 25 - "CentreNotificationsAgent.tsx"
Cohesion: 0.16
Nodes (23): CentreNotificationsAgentProps, CentreNotificationsSuperviseurProps, CreditHistoryTableProps, GroupMembersTableProps, Badge(), badgeVariants, Table(), TableBody() (+15 more)

### Community 26 - "Montant"
Cohesion: 0.15
Nodes (23): calculer_pre_verification(), classe_objet(), PreVerification, `NON_CLASSE` pour tout objet absent de la table active : jamais deviné depuis…, lister_conditions_reexamen(), ParametresReexamen, Cibles utilisées pour transformer un refus en parcours d'éligibilité. Pas de…, Leviers concrets et vérifiables que le sociétaire peut activer. Le refus cesse… (+15 more)

### Community 27 - "ModeleSocle"
Cohesion: 0.10
Nodes (10): EBMScoringModel, Path, ValeurFeature, Charge le champion MLflow, puis un cache vérifié, puis le bundle DVC local., ModeleSocle, DataFrame, Path, Adaptateur pur autour d'un bundle EBM contrôlé. Le nom `ModeleSocle` est… (+2 more)

### Community 28 - "test_registre_et_grille.py"
Cohesion: 0.29
Nodes (14): _connecte(), _payload_grille(), TestClient, test_doublon_version_grille_renvoie_409_puis_une_version_unique_reussit(), test_lecture_grille_autorisee_a_lagent(), test_lecture_grille_autorisee_au_superviseur(), test_marge_hors_bornes_est_rejetee(), test_modification_grille_refusee_a_lagent() (+6 more)

### Community 29 - "Connectivité faible et connecteur de données réel"
Cohesion: 0.05
Nodes (39): Après le pilote, Architecture de déploiement retenue, Ce que signifie « manque de connexion », Comportement retenu pendant une coupure d'agence, Connecteur de données réel, Connectivité faible et connecteur de données réel, Corrections à appliquer à la note de présentation, Critère de réussite national (+31 more)

### Community 30 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 31 - "dependencies.py"
Cohesion: 0.14
Nodes (22): AccessTokenDatabase, AccessToken, get_strategy(), DatabaseStrategy, UUID, current_active_user(), Request, SQLAlchemyAccessTokenDatabase (+14 more)

### Community 32 - "CoreSimPostgresReader"
Cohesion: 0.13
Nodes (14): CoreSimPostgresReader, date, ProduitCredit, SocietaireSearchResult, Implémentation du port `CoreSimReader` contre le schéma réel produit par…, core_sim_reader(), fixture, test_capital_restant_du_est_nul_pour_un_credit_solde() (+6 more)

### Community 33 - "adapters.py"
Cohesion: 0.12
Nodes (30): Engine, Implémente `FicheArchiveeRepository` contre `fiche_archivee` (schéma `solida`)., SqlFicheArchiveeRepository, Implémente `FicheRepository` contre la passerelle S3 de SeaweedFS — pas MinIO,…, SeaweedfsFicheRepository, AuthenticateSocietaire, audit_log(), _client_seaweedfs() (+22 more)

### Community 34 - "DecisionAEnregistrer"
Cohesion: 0.16
Nodes (14): datetime, Engine, Implémente `DecisionRepository` contre `decision_scoring` (schéma `solida`).…, SqlDecisionRepository, decomposition_from_json(), decomposition_to_json(), Any, Conversion entre les lignes SQL et les décisions du domaine. (+6 more)

### Community 35 - "entrainement.py"
Cohesion: 0.18
Nodes (24): ExplainableBoostingClassifier, _calibrer_si_necessaire(), _comparer_ponderation(), _creer_ebm(), _entrainer_ebm(), entrainer_reference_logistique(), _fit_ebm(), _jeu_par_split() (+16 more)

### Community 36 - "Étapes"
Cohesion: 0.11
Nodes (18): 10. Scorecard et décomposition, 11. Contrôle de non-discrimination, 12. Promotion, 1. Chargement et instantané, 2. Définition de la cible, 3. Découpage temporel, 4. Construction des features à `date_reference`, 5. Contrôle des fuites (+10 more)

### Community 37 - "ProbabiliteDefaut"
Cohesion: 0.16
Nodes (23): Adaptateur du bundle EBM SOCLE vers le port métier de scoring., calculer_plafond(), _modulation_risque(), ParametresProgressif, Borne le montant recommandé par le principe du crédit progressif.…, Réglage du crédit progressif — voir docs/formules/., calculer_trajectoire(), Palier indicatif au prochain cycle, à profil de risque inchangé — jamais une… (+15 more)

### Community 38 - "mappers/__init__.py"
Cohesion: 0.20
Nodes (12): Conversion des value objects du domaine vers les schémas pydantic exposés en…, demande_to_notification(), produit_to_schema(), ProduitCredit, decision_to_registre(), decision_a_enregistrer_to_resultat_scoring(), decision_to_resultat_scoring(), ScoringResult (+4 more)

### Community 39 - "De la probabilité au score, et du score à la décision"
Cohesion: 0.12
Nodes (15): Au-delà du refus : conditions de réexamen actionnables, Calibration, Chaîne complète, Connexion à la grille : ce n'est pas un mécanisme séparé, De la probabilité au score, et du score à la décision, Décomposition exacte en points, Garde-fous, Grille de décision (+7 more)

### Community 40 - "calculer_features_groupe"
Cohesion: 0.18
Nodes (25): test_features_groupe_identiques_entre_entrainement_et_inference(), AppartenanceGie, calculer_features_groupe(), CreditGroupeAnterieur, FeaturesGroupe, _mois_avant(), _mois_ecoules(), date (+17 more)

### Community 41 - "authenticate_societaire.py"
Cohesion: 0.24
Nodes (11): _prenom(), ResultatAuthentification, generer_jeton(), Jeton signé, sans état côté serveur (pas de table de session) : le contenu…, None si le jeton est absent, malformé, falsifié ou expiré., _signature(), verifier_jeton(), test_un_jeton_expire_est_rejete() (+3 more)

### Community 42 - "ModeCalcul"
Cohesion: 0.18
Nodes (24): date, Décide SOCLE vs enrichi (`cascade.determiner_mode`) à partir de l'historique…, ContexteCascade, determiner_mode(), ParametresCascade, Seuils d'éligibilité au mode enrichi. Ajustable par la coopérative., Applique les quatre conditions du mode enrichi, dans l'ordre de leur…, Ce qu'il faut savoir sur le groupe d'un sociétaire pour choisir le modèle. Le… (+16 more)

### Community 43 - "Composants tiers et logiciels libres"
Cohesion: 0.22
Nodes (8): Backend (développement, test, construction ; hors chemin d'exécution), Backend et API (exécution), Composants tiers et logiciels libres, Frontend (développement, construction, test ; hors chemin d'exécution), Frontend (exécution), Infrastructure, images Docker de base, Note sur la LGPL (psycopg et psycopg2-binary), Simulateur, générateur de données synthétiques (exécution)

### Community 44 - "demarrer.sh"
Cohesion: 0.32
Nodes (14): attendre_disponibilite(), banniere(), conclure(), configurer_env(), construire_images(), demarrer_services(), echouer(), etape() (+6 more)

### Community 45 - "pipeline.py"
Cohesion: 0.06
Nodes (40): main(), Pont DVC vers le générateur CORE-SIM existant, sans dupliquer sa logique., ajouter_mouvements_nantissement(), charger_config(), choc_a_date(), construire_echeancier_theorique(), construire_soldes_mensuels(), _dates_echeances() (+32 more)

### Community 46 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 47 - "ScoringResult"
Cohesion: 0.13
Nodes (16): DecisionsTable(), DecisionsTableProps, FactorsPanelProps, DecisionRegistreVue, RegistreDecisions(), RegistreDecisionsProps, RegistryFilters(), ScoringResultViewProps (+8 more)

### Community 48 - "demarrer.ps1"
Cohesion: 0.30
Nodes (12): Build-Images(), Initialize-Donnees(), Invoke-Etape(), New-Secret(), Set-Configuration(), Show-Etape(), Show-Info(), Show-Ok() (+4 more)

### Community 49 - "Évaluation"
Cohesion: 0.13
Nodes (14): Analyse par segment, Calibration, Ce qui est présenté au jury, Contrôle de non-discrimination, Courbe de coût et impact financier (métrique de démonstration), Discrimination, Les quatre pièges d'évaluation à éviter (spécifique microfinance), Métriques opérationnelles (+6 more)

### Community 50 - "frontend/lib/services/error-service.ts"
Cohesion: 0.07
Nodes (40): PagePrevisualisationScoring(), handleConfirm(), CentreNotificationsAgent(), confirmer(), ecarter(), CentreNotificationsSuperviseur(), assigner(), ChangePasswordForm() (+32 more)

### Community 51 - "test_societaires.py"
Cohesion: 0.24
Nodes (14): client_agent(), fixture, TestClient, societaire_agence_agent(), societaire_autre_agence(), test_dossier_dun_societaire_de_son_agence_est_accessible(), test_dossier_dun_societaire_dune_autre_agence_est_refuse(), test_dossier_introuvable_renvoie_404() (+6 more)

### Community 52 - "Décisions provisoires à revoir"
Cohesion: 0.13
Nodes (14): Ajustement du générateur CORE-SIM, Approximations de l'adaptateur CORE-SIM, Auto-contrôle multi-octroi (pentest round 3, finding 12), Blocage connu : `next build` (image `front` de production), Décisions provisoires à revoir, Immutabilité des paramètres scorecard via l'API (pentest round 3, finding 9), Le modèle lui-même, `ModeleConstant.contributions()` : décomposition factice, PAS apprise (+6 more)

### Community 53 - "UtilisateurResume"
Cohesion: 0.19
Nodes (8): Any, Engine, _row_to_utilisateur(), SqlUtilisateurRepository, ListerAgentsAgence, Protocol, UtilisateurRepository, UtilisateurResume

### Community 54 - "_decomposition_to_schema"
Cohesion: 0.16
Nodes (17): _Definition, explication(), famille(), formater_valeur(), libelle(), Traduction des codes de variables du modèle vers ce qu'un agent doit lire à…, Phrase de jugement seule : l'appelant affiche déjà `{libelle} : {valeur}` juste…, sens() (+9 more)

### Community 55 - "scorer_demande.py"
Cohesion: 0.13
Nodes (32): _avertissement_montant_reduit_objet_non_divisible(), _actualiser_features(), _features_to_dict(), _features_to_dict_enrichi(), Calcule les ratios de la demande actuelle sans ajouter de charge externe. Les…, Préserve catégories et absences : EBM les interprète nativement., Catalogue enrichi : les 20 features SOCLE plus la couche solidaire (groupe…, _revenu_effectif() (+24 more)

### Community 56 - "frontend-societaire/components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 57 - "Formule cible du crédit progressif — à activer quand le modèle EBM réel existe"
Cohesion: 0.12
Nodes (16): 10. Corrections apportées — résumé, 1. Formule maîtresse, 2. L'ancre de capacité prouvée ($M$), 3. Le taux de variation lissé ($\delta_N$), 4. Les garde-fous, 5. Amorçage — premier prêt ($N=1$, pas d'historique), 6. Projection au prochain cycle — remplace `calculer_trajectoire`, 7. Paramètres — aucun n'est calibré, tous à trancher par rétro-test (+8 more)

### Community 58 - "Sélection de variables et prétraitement — principes"
Cohesion: 0.15
Nodes (12): Ce qu'on n'utilise pas, et pourquoi (choix assumé, défendable devant le jury), Contraintes de monotonie (optionnel, P2), La redondance survit, même sans VIF, Les interactions : EBM les trouve, on ne les fabrique pas à la main, Mais les variables construites restent le cœur : EBM ne les invente pas, Méthode de sélection retenue : l'importance native d'EBM, Protection métier et réglementaire, Périmètre hackathon (+4 more)

### Community 59 - "core_sim_postgres_reader.py"
Cohesion: 0.10
Nodes (14): Engine, PostgresEpargneReader, date, Engine, PostgresGarantieReader, Engine, PostgresProduitReader, Engine (+6 more)

### Community 60 - "errors.py"
Cohesion: 0.10
Nodes (25): ProcessSocietaireDemande, ResultatDemandeSocietaire, DomainError, DonneesInsuffisantes, IdentiteSocietaireInvalide, ModeleIndisponible, MontantDemandeInvalide, Aucun sociétaire ne correspond à l'identifiant fourni. (+17 more)

### Community 61 - "feature_store_core_sim.py"
Cohesion: 0.16
Nodes (18): FeatureStoreCoreSim, _max_jours_retard(), _mois_ecoules(), _montant_max_rembourse(), _nb_incidents_anterieurs(), date, Calcule une ancienneté à la date de décision, jamais à l'instant présent., Plus grand montant correctement remboursé, feature historique du SOCLE. (+10 more)

### Community 62 - "connexion/page.tsx"
Cohesion: 0.32
Nodes (4): LogoAnime(), CHEMINS, PARTICULES, SavingsFlowBeam()

### Community 63 - "MLflow"
Cohesion: 0.17
Nodes (11): Artefacts, Ce qui est journalisé à chaque exécution, Configuration, Discipline, MLflow, Métriques, Organisation des expériences, Paramètres (+3 more)

### Community 64 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, start, test, typecheck

### Community 65 - "dependencies"
Cohesion: 0.11
Nodes (19): dependencies, class-variance-authority, clsx, lucide-react, next, radix-ui, react, react-dom (+11 more)

### Community 66 - "metrics.py"
Cohesion: 0.20
Nodes (10): courbe_precision_rappel(), ecart_maximal_deciles(), erreur_calibration_attendue(), DataFrame, ndarray, Métriques de discrimination, calibration et recommandation., ECE pondérée en classes de probabilité de même largeur., Écart observé/prédit dans des déciles de population, pas de largeur fixe. (+2 more)

### Community 67 - "ScoringModel"
Cohesion: 0.22
Nodes (5): Protocol, ValeurFeature, Retourne `(code_variable, contribution_log_odds)` pour chaque variable. Liste…, Contrat d'un modèle explicable, indépendant de son stockage ou de MLflow., ScoringModel

### Community 68 - "frontend/package.json"
Cohesion: 0.17
Nodes (12): engines, node, lint-staged, *.{json,css,md}, *.{ts,tsx,js,jsx,mjs}, name, overrides, @vitest/mocker (+4 more)

### Community 69 - "Éthique de la décision automatisée"
Cohesion: 0.20
Nodes (9): 1. Exclusion des variables sensibles, 2. Contrôle des substituts, 3. Explicabilité de droit, 4. Décision humaine finale, 5. Souveraineté des données, 6. Droit à la contestation, 7. Ce que nous refusons explicitement, 8. Mention obligatoire (+1 more)

### Community 70 - "DVC — versionnage des données et des modèles"
Cohesion: 0.20
Nodes (9): Ce qui est versionné avec DVC, DVC — versionnage des données et des modèles, Licence et pérennité, Pipeline reproductible, Pourquoi DVC ici et pas autre chose, Périmètre hackathon, Remote : MinIO, mutualisé, Reproductibilité complète, avec MLflow (+1 more)

### Community 71 - ".prettierrc.json"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 72 - "Protocole obligatoire pour les agents (Claude Code, Codex)"
Cohesion: 0.18
Nodes (10): 1. Règle zéro : ne jamais inventer une décision, 2. Protocole de recherche obligatoire avant décision technique, 3. Périmètre et frontières, 4. Ordre de travail imposé, 5. Interdits absolus, 6. Style de production attendu, 7. Communication, 8. Rappel du contexte produit (+2 more)

### Community 89 - "test_notifications.py"
Cohesion: 0.35
Nodes (12): _connecter(), _creer_demande_nouvelle(), _ids_notifications(), TestClient, J2 (clôture) : le routage des notifications passe désormais par le superviseur…, Un superviseur d'agence ne doit jamais pouvoir consulter une autre agence en…, test_agent_ne_peut_pas_assigner(), test_flux_complet_superviseur_assigne_puis_agent_traite() (+4 more)

### Community 91 - "Protocole obligatoire pour les agents (Claude Code, Codex)"
Cohesion: 0.20
Nodes (9): 1. Règle zéro : ne jamais inventer une décision, 2. Protocole de recherche obligatoire avant décision technique, 3. Périmètre et frontières, 4. Ordre de travail imposé, 5. Interdits absolus, 6. Style de production attendu, 7. Communication, 8. Rappel du contexte produit (+1 more)

### Community 110 - "DonneesGroupeBrutes"
Cohesion: 0.16
Nodes (14): PostgresDonneesGroupeReader, Engine, `None` si `gie_id` ne correspond à aucun groupe connu. Historique complet du…, DonneesGroupeBrutes, Ce que `CoreSimReader.charger_donnees_groupe` doit fournir pour que…, donnees_groupe_reader(), fixture, _credits_de_groupe() (+6 more)

### Community 121 - "postgres_credit_reader.py"
Cohesion: 0.27
Nodes (7): _capital_restant_du(), PostgresCreditReader, Any, date, Engine, Approxime le capital restant dû. CORE-SIM ne fournit pas d'échéancier : la…, _row_to_credit()

### Community 122 - "Feature engineering"
Cohesion: 0.22
Nodes (8): Ce que nous ne faisons pas, Documentation obligatoire, Feature engineering, Règle absolue, Traitement des catégories, Variables de conditions sectorielles (micro-économie observée) — P1/P2, Variables de la couche solidaire (segment de groupe), Variables du socle individuel

### Community 123 - "AccessLoggingMiddleware"
Cohesion: 0.29
Nodes (5): AccessLoggingMiddleware, Request, Response, Remplace le journal d'accès en texte brut d'uvicorn (désactivé via `--no-…, BaseHTTPMiddleware

### Community 124 - "_inserer_evenement_test"
Cohesion: 0.53
Nodes (5): _inserer_evenement_test(), Connection, UUID, test_solida_app_ne_peut_ni_modifier_ni_supprimer_journal_audit(), test_solida_purge_sans_le_flag_de_session_ne_peut_pas_supprimer()

### Community 125 - "Cascade et démarrage à froid"
Cohesion: 0.22
Nodes (8): Cascade et démarrage à froid, Cohérence entre les deux modèles, Conditions précises du mode enrichi, Le problème, Logique de sélection, Motifs de bascule, restitués à l'agent, Repli en cas de panne, Traitement du primo-emprunteur

### Community 126 - "Leçons du prototype simulateur (retiré)"
Cohesion: 0.22
Nodes (8): 1. Fuite temporelle du bloc épargne, 2. Coefficient documenté comme protecteur, jamais câblé, 3. Formule d'échéance simplifiée à l'excès, code mort laissé en place, Ce que chacun visait, et où c'est traité maintenant, Ce qui a échoué — à ne pas reproduire, Contexte, Leçons du prototype simulateur (retiré), Pour la suite

### Community 127 - "Détection de dérive"
Cohesion: 0.22
Nodes (8): Alertes, Détection de dérive, Fréquence, Indice de stabilité de population (PSI), Le décalage temporel, difficulté propre au crédit, Outil, Périmètre hackathon, Trois types de dérive

### Community 128 - "Cas d'usage et routeurs HTTP"
Cohesion: 0.22
Nodes (8): Cas d'usage et routeurs HTTP, Cloisonnement par agence : sur l'agent qui agit, pas sur le sociétaire visé, `decision_scoring.resultat_complementaire`, Endpoints, alignés sur le contrat frontend existant, Persistance JSONB avec psycopg 3 : `bindparams(type_=JSONB)` obligatoire, Rôles autorisés par endpoint, `ScorerDemande` : features de profil vs. features de la demande, `utilisateur.agence_id` doit être un vrai code CORE-SIM

### Community 129 - "Transmission complète — SOLIDA"
Cohesion: 0.22
Nodes (9): Bundle, backend et MLOps, Données disponibles pour l'enrichi, Décisions terrain prioritaires, EBM, déséquilibre et métriques, Enrichi et moteur de décision : réponses/blocages, Réconciliation avec l'historique, SOCLE EBM : spécification figée, Transmission complète — SOLIDA (+1 more)

### Community 130 - "Contrats et implémentations factices"
Cohesion: 0.22
Nodes (8): Authentification de démonstration, Bascule vers le backend réel (task #33) — ce qui doit changer, et rien d'autre, Cas fixtures, Contrats et implémentations factices, Décision persistée par identifiant opaque (`decision_id`), Fichiers, Moteur de scoring factice, Écart avec le contrat gelé — résolu (ADR-019)

### Community 131 - "Docker et développement"
Cohesion: 0.22
Nodes (8): Bug connu en amont : panique Turbopack en HMR (mode dev uniquement), Ce que démarre `docker compose up`, Ce qui n'existe pas encore dans `docker-compose.yml`, Commandes disponibles, Docker et développement, Dockerfile, Développement local (rechargement à chaud), Sécurité du conteneur

### Community 132 - "equite.py"
Cohesion: 0.28
Nodes (8): ecarts_a_risque_comparable(), DataFrame, rapport_par_strate(), Rapports de performance et d'équité, séparés de la matrice de prédiction., Agrège les probabilités et défauts par strates de revue humaine., Mesure les écarts de score par sexe et zone dans chaque décile de risque. Aucun…, Signale un écart supérieur à cinq points, sans supprimer de variable., seuil_revue_humaine()

### Community 133 - "Principes de modélisation"
Cohesion: 0.25
Nodes (7): Ce qui est interdit, Déséquilibre de classes, Les quatre modèles, Pourquoi l'EBM, Principes de modélisation, Reproductibilité, Variable cible

### Community 134 - "Cycle de vie du modèle"
Cohesion: 0.25
Nodes (7): Contrôles de promotion, Cycle de vie du modèle, Les six étapes, Promotion et retrait, Reproductibilité, Retour arrière, Versionnage

### Community 135 - "Monitoring et mise en production"
Cohesion: 0.25
Nodes (7): Ce qu'on surveille, par question posée, Déploiement, Monitoring et mise en production, Périmètre hackathon, Reprise après incident, Sauvegarde, Seuils d'alerte

### Community 136 - "SOLIDA"
Cohesion: 0.25
Nodes (7): Architecture, Comptes de démonstration, Documentation technique, Démarrage, Démarrage manuel (détail de ce que fait le script, ou pour aller pas à pas), Développement local, SOLIDA

### Community 137 - "Politique de crédit — décisions en attente"
Cohesion: 0.29
Nodes (6): Décision en attente : préréglages « Prudent / Équilibré / Expansion contrôlée », Décision en attente : seuil d'alerte sur le volume de lecture (recherche/dossier sociétaire), Méthodologie de calibrage d'un seuil de décision (recherche externe), Politique de crédit — décisions en attente, Périmètre administrateur modèle : confirmé hors SOLIDA, Statut actuel des paramètres (rappel, détail dans `docs/backend/03-decisions-provisoires-a-revoir.md`)

### Community 138 - "Câblage frontend → backend réel"
Cohesion: 0.29
Nodes (6): Câblage frontend → backend réel, Retiré, Réécriture, pas de proxy applicatif, Server Components : le cookie ne traverse pas tout seul, Vérifié, Écrans corrigés au passage

### Community 139 - "continuite/README.md"
Cohesion: 0.29
Nodes (3): Donner le contexte à un nouvel agent, Reprendre SOLIDA sur un autre PC, Questionnaire suivi — modèle enrichi et moteur de décision

### Community 140 - "Sécurité — mesures appliquées"
Cohesion: 0.29
Nodes (6): Conteneurs, En-têtes HTTP, Hors périmètre de cette passe, Secrets, Session, Sécurité — mesures appliquées

### Community 141 - "Postgres et simulateur CORE-SIM"
Cohesion: 0.29
Nodes (6): Démarrer, Garde-fou vérifié, Postgres et simulateur CORE-SIM, Services, Sécurité des conteneurs Postgres, Écart de schéma

### Community 142 - "modelisation/README.md"
Cohesion: 0.29
Nodes (3): Artefacts attendus, Reprendre sur une autre machine, Transmission du module de modélisation

### Community 143 - "Model card — SOCLE EBM"
Cohesion: 0.29
Nodes (7): Cible et population, Features, Gouvernance, Limites, Model card — SOCLE EBM, Sorties, Usage prévu

### Community 144 - "montant_maximal_supportable"
Cohesion: 0.21
Nodes (12): montant_maximal_supportable(), Plus grand montant dont la mensualité actuarielle ne dépasse pas…, test_montant_maximal_a_taux_zero_est_mensualite_fois_duree(), test_montant_maximal_augmente_avec_la_duree(), test_montant_maximal_avec_revenu_nul_est_zero(), test_montant_maximal_croit_avec_le_revenu(), test_montant_maximal_respecte_exactement_le_ratio_a_la_reconstitution(), mensualite_actuarielle() (+4 more)

### Community 145 - "SOLIDA -- Generateur CORE-SIM v4"
Cohesion: 0.29
Nodes (6): Decisions terrain J1-05 a J1-13, Frontiere avec le modele, Produits et taux annuels, SOLIDA -- Generateur CORE-SIM v4, Sorties, Utilisation et validation

### Community 146 - "Rôles applicatifs vs organigramme réel (CEF-MF Lomé)"
Cohesion: 0.33
Nodes (5): Autres écarts notés, non urgents, Décision en attente : faut-il un rôle `chef_agence` ?, Rapprochement avec les 4 rôles actuels, Rôles applicatifs vs organigramme réel (CEF-MF Lomé), Écart principal : aucun rôle scopé à une seule agence en supervision

### Community 147 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, start, test, typecheck

### Community 148 - "Persistance et migrations"
Cohesion: 0.33
Nodes (5): Authentification : tables FastAPI-Users renommées, `decision_scoring` : garde-fou en base, pas seulement applicatif, Grille et progressif : paramétrables en base, pas dans le code, Persistance et migrations, Schéma `solida` (Alembic, migration initiale)

### Community 149 - "Journal de discussion conservé pour reprise"
Cohesion: 0.40
Nodes (5): Générateur J1-05 à J1-13, Journal de discussion conservé pour reprise, Provenance, SOCLE EBM J1-14 à J1-21, Suite demandée

### Community 150 - "Hooks Git et CI"
Cohesion: 0.33
Nodes (5): Activation (une fois par clone), Ce qui manque volontairement, CI, Hooks, Hooks Git et CI

### Community 151 - "orm_models/__init__.py"
Cohesion: 0.24
Nodes (11): run_migrations_offline(), run_migrations_online(), url_migration(), AuditEvent, Base, DecisionScoring, FicheArchivee, Métadonnées seulement — le PDF lui-même vit dans le stockage objet (SeaweedFS),… (+3 more)

### Community 152 - "test_lister_notifications.py"
Cohesion: 0.31
Nodes (7): _demande(), _FakeCoreSimReader, _FakeDemandeSocietaireRepository, _societaire(), test_agent_ne_voit_que_ses_demandes_assignees(), test_superviseur_dagence_ne_voit_que_les_non_assignees_de_son_agence(), test_superviseur_reseau_voit_les_non_assignees_de_toutes_les_agences()

### Community 153 - "Scaffold backend et outillage Python"
Cohesion: 0.40
Nodes (4): Arborescence, Docker, Outillage (uv, ruff, mypy, pytest, import-linter), Scaffold backend et outillage Python

### Community 154 - "Adaptateur CORE-SIM"
Cohesion: 0.40
Nodes (4): Adaptateur CORE-SIM, Agrégats de groupe : toujours du point de vue du sociétaire consulté, Colonnes absentes du générateur, estimées à l'affichage, Variables jamais lues

### Community 155 - "Constat Claude — plafonds par produit"
Cohesion: 0.33
Nodes (5): Cause technique lue, Constat Claude — plafonds par produit, Décision et correction appliquées, Historique rapporté par Claude, Symptôme constaté

### Community 156 - "Design system — implémentation"
Cohesion: 0.40
Nodes (4): Ajouter un nouveau jeton, Design system — implémentation, Décisions d'implémentation, Fichiers

### Community 157 - "Calcul de l'échéance mensuelle"
Cohesion: 0.40
Nodes (4): Calcul de l'échéance mensuelle, Ce qui reste à trancher, Méthode retenue, Pourquoi

### Community 158 - "Décisions techniques SOCLE"
Cohesion: 0.40
Nodes (5): Décisions métier déjà reçues, Décisions techniques SOCLE, Décisions volontairement différées, Déséquilibre de classes, Sources vérifiées — 13 septembre 2026

### Community 159 - "Modélisation SOCLE SOLIDA"
Cohesion: 0.40
Nodes (5): Commandes locales, Conteneurs, Flux reproductible, Garanties de temporalité, Modélisation SOCLE SOLIDA

### Community 163 - "devDependencies"
Cohesion: 0.11
Nodes (19): devDependencies, eslint, eslint-config-next, prettier, tailwindcss, @tailwindcss/postcss, tw-animate-css, @types/react-dom (+11 more)

### Community 168 - "valider_mot_de_passe"
Cohesion: 0.40
Nodes (9): MotDePasseInvalide, Le mot de passe proposé ne respecte pas la politique en vigueur., Lève `MotDePasseInvalide` si une règle est violée ; ne renvoie rien sinon.…, valider_mot_de_passe(), test_la_comparaison_a_la_liste_courante_ignore_la_casse(), test_un_mot_de_passe_conforme_ne_leve_rien(), test_un_mot_de_passe_courant_est_refuse(), test_un_mot_de_passe_trop_court_est_refuse() (+1 more)

### Community 170 - "Authentification"
Cohesion: 0.25
Nodes (7): Authentification, Endpoints, FastAPI-Users, session révocable unique, Politique de mot de passe, Provisioning et cycle de vie des comptes, Rôles et cloisonnement, Simplification à noter

### Community 171 - "AccesRefuse"
Cohesion: 0.44
Nodes (15): AssignerNotification, AccesRefuse, L'acteur courant n'a pas les droits nécessaires pour cette action., _agent(), _demande(), _FakeDemandeSocietaireRepository, _FakeUtilisateurRepository, test_assignation_reussie_meme_agence() (+7 more)

### Community 172 - "proxy.ts"
Cohesion: 0.40
Nodes (5): SESSION_COOKIE, config, proxy(), ROUTES_PROTEGEES, toLogin()

### Community 173 - "onSubmit"
Cohesion: 0.50
Nodes (3): LoginForm(), onSubmit(), safeRelativePath()

### Community 174 - "Convention de nommage technique (refactor SOLID / anglicisation)"
Cohesion: 0.25
Nodes (7): Adaptateurs concrets, Autres décisions, Ce qui ne change pas, Convention de nommage technique (refactor SOLID / anglicisation), Décision, Ports (`domain/ports/`), Routeurs et authentification

### Community 175 - "Societaire"
Cohesion: 0.15
Nodes (9): date, datetime, Coercion de date partagée entre les lecteurs CORE-SIM. CORE-SIM stocke…, vers_date(), PostgresSocietaireReader, Engine, SocietaireSearchResult, Instantané des données brutes CORE-SIM pour un sociétaire. Ne porte jamais le… (+1 more)

### Community 176 - "test_features.py"
Cohesion: 0.83
Nodes (3): _tables(), test_features_excluent_les_colonnes_interdites(), test_mouvements_futurs_n_affectent_pas_feature_historique()

### Community 178 - "test_consulter_dossier.py"
Cohesion: 0.14
Nodes (14): PostgresGroupeReader, Engine, GroupeCaution, MembreGroupe, Snapshot du groupe, calculé du point de vue d'un sociétaire donné. Les agrégats…, _credit(), _FakeCoreSimReader, _groupe() (+6 more)

### Community 179 - "archiver_fiche.py"
Cohesion: 0.14
Nodes (11): ArchiverFiche, GenererFiche, FicheRepository, Protocol, Stockage objet des fiches PDF archivées — jamais en base (`solida` reste léger)., AuditLog, Protocol, Chaque entrée : acteur, action, objet, horodatage. Jamais de mot de passe,… (+3 more)

### Community 181 - "SoldeMensuelEpargne"
Cohesion: 0.21
Nodes (16): date, calculer_features_epargne(), FeaturesEpargne, _premier_jour_mois(), date, Trajectoire d'épargne : fonctions pures partagées entre entraînement et…, Utilise seulement les mois totalement clos avant `date_reference`. `soldes` n'a…, SoldeMensuelEpargne (+8 more)

### Community 183 - "routers/registre.py"
Cohesion: 0.25
Nodes (7): PageRegistre, BaseModel, ListerDecisions, DecisionRegistreAffichee, `DecisionEnregistree` enrichie du nom et de l'agence du sociétaire (CORE-SIM),…, lister(), get

### Community 184 - "DemandeSocietaire"
Cohesion: 0.10
Nodes (12): NoopNotificationSender, Canal externe reporté (email ou autre, décision explicite) : log seulement,…, Any, _row_to_demande(), SqlDemandeSocietaireRepository, DemandeSocietaireRepository, Protocol, NotificationSender (+4 more)

### Community 185 - "ArchiverNotification"
Cohesion: 0.38
Nodes (7): ArchiverNotification, _demande(), _FakeDemandeSocietaireRepository, test_demande_introuvable_renvoie_none(), test_refus_si_agence_differente(), test_refus_si_lagent_nest_pas_lassigne(), test_succes_si_lagent_est_lassigne()

### Community 186 - "mesurer_apport_couche_solidaire"
Cohesion: 0.29
Nodes (12): ApportCoucheSolidaire, mesurer_apport_couche_solidaire(), _population_credits_de_groupe_test(), DataFrame, Mesure de l'apport de la couche solidaire (J2-04). Compare le modèle enrichi au…, `dataset` est le jeu enrichi complet (pour retrouver les crédits de groupe du…, _dataset(), _predictions() (+4 more)

### Community 187 - "RecommendationPanel.tsx"
Cohesion: 0.07
Nodes (47): NumberTicker(), PolicyPreset, PolitiqueCredit(), PolitiqueCreditProps, RecommendationPanel(), RecommendationPanelProps, ScoringResultView(), Section() (+39 more)

### Community 188 - "grille_repository_sql.py"
Cohesion: 0.20
Nodes (11): _configuration_to_thresholds(), Any, ConfigurationGrille, Engine, Implémente `GrilleRepository` contre `grille_decision` (schéma `solida`)., _row_to_configuration(), SqlGrilleRepository, Une configuration de grille porte déjà ce `version_grille`. (+3 more)

### Community 189 - "post-commit"
Cohesion: 0.40
Nodes (4): post-commit script, GRAPHIFY_CHANGED, GRAPHIFY_REBUILD_LOG, PYTHONHASHSEED

### Community 190 - "frontend/app/layout.tsx"
Cohesion: 0.29
Nodes (6): ibmPlexMono, ibmPlexSans, sourceSerif4, metadata, Toaster(), TooltipProvider()

### Community 191 - "Model card — modèle enrichi (couche solidaire)"
Cohesion: 0.22
Nodes (8): Apport de la couche solidaire (J2-04) — population éligible uniquement, Cible et population, Comparatif à trois modèles (test ≥ 2024, mêmes lignes), Features, Gouvernance, Limites (en plus de celles du SOCLE), Model card — modèle enrichi (couche solidaire), Usage prévu

### Community 192 - "cli.py"
Cohesion: 0.19
Nodes (16): auditer_risque_fuite(), Any, DataFrame, Contrôles explicites avant toute revue d'un modèle SOCLE., Produit une preuve d'audit, sans dissimuler une performance anormalement élevée., codes_features_socle(), _commit_git(), main() (+8 more)

### Community 193 - "frontend-societaire/package.json"
Cohesion: 0.25
Nodes (7): engines, node, name, overrides, @vitest/mocker, private, version

### Community 196 - "construire_cible"
Cohesion: 0.29
Nodes (6): construire_cible(), DataFrame, Timestamp, Construction déterministe de la cible de défaut à 30 jours., Retourne les quatre classes, sans lire les issues synthétiques du crédit., test_frontieres_j15_et_j30_et_maturite()

### Community 197 - "devDependencies"
Cohesion: 0.08
Nodes (25): devDependencies, eslint, lint-staged, prettier, shadcn, tailwindcss, @tailwindcss/postcss, tw-animate-css (+17 more)

### Community 199 - "GrilleRepository"
Cohesion: 0.40
Nodes (4): GrilleRepository, ConfigurationGrille, Protocol, La grille est versionnée, jamais modifiée en place :…

### Community 201 - "routers/scoring.py"
Cohesion: 0.17
Nodes (27): FicheJustification, BaseModel, DecisionRegistre, ActualisationSituation, ContributionVariable, PalierProgression, BaseModel, ScoringInput (+19 more)

### Community 203 - "Interroger plusieurs bases hétérogènes en lecture seule (MySQL / Postgres / Oracle)"
Cohesion: 0.33
Nodes (5): Ce qu'on a le droit de faire sans toucher au logiciel existant, Ce qui change par moteur, Interroger plusieurs bases hétérogènes en lecture seule (MySQL / Postgres / Oracle), Principe directeur : un port par source, jamais un accès direct depuis le métier, Règles communes, quel que soit le moteur

### Community 226 - "User"
Cohesion: 0.12
Nodes (22): User, ConsulterDossier, ListerSocietairesRecents, SocietaireSearchResult, Réutilise le journal d'audit plutôt qu'une table de récents dédiée., SocietaireSearchResult, RechercherSocietaire, Authentifie par identifiant sans révéler son existence par le temps de réponse. (+14 more)

### Community 228 - "post-checkout"
Cohesion: 0.50
Nodes (3): post-checkout script, GRAPHIFY_REBUILD_LOG, PYTHONHASHSEED

### Community 248 - "routers/auth.py"
Cohesion: 0.10
Nodes (29): datetime, Engine, Renvoie les objets distincts récents pour alimenter les sociétaires récents., Implémente `AuditLog` contre `journal_audit` (schéma `solida`)., SqlAuditLog, client_ip_address(), Request, Privilégie l’adresse validée par nginx, avec repli pour le développement local. (+21 more)

### Community 269 - "routers/portail.py"
Cohesion: 0.10
Nodes (26): DemandePreVerificationReponse, DemandePreVerificationRequete, BaseModel, VerificationCompteReponse, VerificationCompteRequete, ProduitCredit, BaseModel, ListerProduits (+18 more)

## Knowledge Gaps
- **580 isolated node(s):** `solida-backend`, `DUREES_STANDARD`, `metadata`, `viewport`, `REPERES` (+575 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CoreSimReader` connect `CoreSimReader` to `test_consulter_dossier_mapping.py`, `User`, `adapters.py`, `test_scorer_demande_validations.py`, `values/decision.py`, `authenticate_societaire.py`, `routers/portail.py`, `DonneesGroupeBrutes`, `Societaire`, `test_consulter_dossier.py`, `archiver_fiche.py`, `routers/notifications.py`, `scorer_demande.py`, `routers/registre.py`, `SoldeMensuelEpargne`, `core_sim_postgres_reader.py`, `errors.py`, `feature_store_core_sim.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `Montant` connect `Montant` to `DecisionAEnregistrer`, `ProbabiliteDefaut`, `values/decision.py`, `test_scorer_demande.py`, `errors.py`, `montant_maximal_supportable`, `parametrage.py`, `TrancheDecision`, `scorer_demande.py`, `test_lister_decisions.py`, `test_notifications.py`, `grille_repository_sql.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `AccesRefuse` connect `AccesRefuse` to `routers/auth.py`, `User`, `test_scorer_demande_validations.py`, `solida_engine`, `test_scorer_demande.py`, `routers/scoring.py`, `archiver_fiche.py`, `DemandeSocietaire`, `ArchiverNotification`, `errors.py`, `dependencies.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Montant` (e.g. with `ProcessSocietaireDemande` and `_avertissement_montant_reduit_objet_non_divisible()`) actually correct?**
  _`Montant` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `CoreSimReader` (e.g. with `FeatureStoreCoreSim` and `AuthenticateSocietaire`) actually correct?**
  _`CoreSimReader` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ProbabiliteDefaut` (e.g. with `EBMScoringModel` and `ScoringModel`) actually correct?**
  _`ProbabiliteDefaut` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `solida-backend`, `DUREES_STANDARD`, `metadata` to the rest of the system?**
  _580 weakly-connected nodes found - possible documentation gaps or missing edges._