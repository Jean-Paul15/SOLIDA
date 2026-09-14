# Graph Report - SOLIDA  (2026-09-14)

## Corpus Check
- 461 files · ~186,044 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2758 nodes · 5794 edges · 195 communities (169 shown, 26 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 298 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `961fb928`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- demande-context.tsx
- test_consulter_dossier_mapping.py
- test_scorecard.py
- test_scorer_demande_validations.py
- solida_engine
- feature_store_core_sim.py
- useNewRequest.ts
- session.ts
- test_scorer_demande.py
- frontend/lib/contracts.ts
- cn
- codes_features_socle
- RefreshFields.tsx
- solida_modelisation/features.py
- Monitoring sécurité — applicatif et infrastructure
- FeaturesSolidaires
- test_scoring.py
- cli.py
- compilerOptions
- CoreSimReader
- ConfigurationGrille
- routers/notifications.py
- ProbabiliteDefaut
- dependencies
- test_lister_decisions.py
- CentreNotifications.tsx
- process_societaire_demande.py
- ModeleSocle
- test_registre_et_grille.py
- Connectivité faible et connecteur de données réel
- components.json
- User
- CoreSimPostgresReader
- adapters.py
- DecisionEnregistree
- entrainement.py
- Étapes
- Montant
- ProduitCredit
- De la probabilité au score, et du score à la décision
- PolitiqueCredit.tsx
- verifier_jeton
- ModeCalcul
- Composants tiers et logiciels libres
- demarrer.sh
- pipeline.py
- parametrage.py
- ._calculate
- demarrer.ps1
- Évaluation
- LoginForm.tsx
- test_societaires.py
- Décisions provisoires à revoir
- core_sim.py
- _decomposition_to_schema
- scorer_demande.py
- frontend-societaire/components.json
- Formule cible du crédit progressif — à activer quand le modèle EBM réel existe
- Sélection de variables et prétraitement — principes
- _row_to_credit
- env.py
- MouvementEpargne
- connexion/page.tsx
- MLflow
- scripts
- routers/produits.py
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
- DemandeSocietaire
- Protocole obligatoire pour les agents (Claude Code, Codex)
- postcss.config.mjs
- coresim-init.sh
- solida-init.sh
- charger_postgres.py
- demo_recherche.py
- solida-backend
- plis_temporels_entrainement
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
- mensualite_actuarielle
- SOLIDA -- Generateur CORE-SIM v4
- Rôles applicatifs vs organigramme réel (CEF-MF Lomé)
- SqlFicheArchiveeRepository
- Persistance et migrations
- Journal de discussion conservé pour reprise
- Hooks Git et CI
- orm_models/__init__.py
- mappers/__init__.py
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
- prettier
- shadcn
- 06-outils.md
- frontend/README.md
- errors.py
- data/README.md
- Authentification
- FeatureStoreCoreSim
- SeaweedfsFicheRepository
- SocietaireSearchResult
- Convention de nommage technique (refactor SOLID / anglicisation)
- SocietaireSearchResult
- SocietaireSearchResult
- MembreGroupe
- RecommendationPanel.tsx
- post-commit
- frontend-societaire/package.json
- test_executer_compose_le_dossier_complet
- devDependencies
- routers/scoring.py
- routers/societaires.py
- post-checkout
- routers/auth.py
- routers/portail.py
- ThresholdsTab.tsx
- frontend-societaire/eslint.config.mjs
- frontend-societaire/next.config.ts
- frontend-societaire/postcss.config.mjs

## God Nodes (most connected - your core abstractions)
1. `cn()` - 101 edges
2. `ProbabiliteDefaut` - 48 edges
3. `Montant` - 46 edges
4. `User` - 41 edges
5. `CoreSimReader` - 37 edges
6. `DecisionEnregistree` - 34 edges
7. `_build_use_case()` - 33 edges
8. `AccesRefuse` - 30 edges
9. `CoreSimPostgresReader` - 26 edges
10. `DecisionAEnregistrer` - 24 edges

## Surprising Connections (you probably didn't know these)
- `_membre()` --calls--> `MembreGroupe`  [EXTRACTED]
  backend/tests/application/test_consulter_dossier.py → frontend/lib/contracts.ts
- `include` --extends--> `next-env.d.ts`  [EXTRACTED]
  frontend/tsconfig.json → frontend-societaire/tsconfig.json
- `include` --extends--> `**/*.ts`  [EXTRACTED]
  frontend/tsconfig.json → frontend-societaire/tsconfig.json
- `include` --extends--> `**/*.tsx`  [EXTRACTED]
  frontend/tsconfig.json → frontend-societaire/tsconfig.json
- `include` --extends--> `.next/types/**/*.ts`  [EXTRACTED]
  frontend/tsconfig.json → frontend-societaire/tsconfig.json

## Import Cycles
- None detected.

## Communities (195 total, 26 thin omitted)

### Community 0 - "demande-context.tsx"
Cohesion: 0.05
Nodes (61): BonjourPage(), ConfirmationPage(), CHOIX, DureePage(), ibmPlexMono, ibmPlexSans, sourceSerif4, metadata (+53 more)

### Community 1 - "test_consulter_dossier_mapping.py"
Cohesion: 0.06
Nodes (57): PostgresEpargneReader, date, Engine, MouvementEpargne, PostgresGroupeReader, Engine, dossier_to_schema(), groupe_to_schema() (+49 more)

### Community 2 - "test_scorecard.py"
Cohesion: 0.15
Nodes (22): InvariantScoreViole, La décomposition en points ne somme pas au score : le scoring est rejeté., calculer_score(), decomposer_en_points(), ParametresScorecard, Mise à l'échelle probabilité de défaut -> score, par transformation PDO — voir…, Transforme une probabilité de défaut en score. Convention bancaire : score…, Répartit un log-odds en points de base et contributions par variable. Suppose… (+14 more)

### Community 3 - "test_scorer_demande_validations.py"
Cohesion: 0.10
Nodes (41): datetime, ProduitCredit, valider_acces_agence(), valider_duree_dans_bornes(), valider_montant_sous_plafond_institutionnel(), valider_pas_de_credit_en_cours(), valider_pas_de_multi_octroi(), valider_produit_catalogue() (+33 more)

### Community 4 - "solida_engine"
Cohesion: 0.06
Nodes (65): ArgumentParser, alert(), AlertedActor, detect(), _main(), datetime, Alerte les pics de lecture sans bloquer automatiquement les comptes. Le seuil…, Renvoie les acteurs au-dessus du seuil, sans écrire. (+57 more)

### Community 5 - "feature_store_core_sim.py"
Cohesion: 0.20
Nodes (15): _max_jours_retard(), _mois_ecoules(), _mois_suivant(), _montant_max_rembourse(), _nb_incidents_anterieurs(), _premier_jour_mois(), date, MouvementEpargne (+7 more)

### Community 6 - "useNewRequest.ts"
Cohesion: 0.09
Nodes (29): PagePrevisualisationScoring(), handleConfirm(), EconomicActivityPanelProps, FicheApercu(), FicheApercuProps, NouvelleDemandeSheet(), NouvelleDemandeSheetProps, DUREES_STANDARD (+21 more)

### Community 7 - "session.ts"
Cohesion: 0.11
Nodes (30): AppLayout(), PageNotifications(), PageGrille(), PageRegistre(), PageFiche(), PageFicheProps, PageResultatScoring(), PageResultatScoringProps (+22 more)

### Community 8 - "test_scorer_demande.py"
Cohesion: 0.12
Nodes (27): _build_use_case(), _configuration(), _demande(), _FakeAuditLog, _FakeCoreSimReader, _FakeDecisionRepository, _FakeGrilleRepository, _FakeScoringModel (+19 more)

### Community 9 - "frontend/lib/contracts.ts"
Cohesion: 0.08
Nodes (35): LIBELLE_SEGMENT, CreditHistoryTable(), EconomicActivityPanel(), GuaranteePanel(), GuaranteePanelProps, LoanSummary(), LoanSummaryProps, LIBELLE_NIVEAU_INSTRUCTION (+27 more)

### Community 10 - "cn"
Cohesion: 0.05
Nodes (59): GroupeCautionDialogProps, GroupMembersTable(), RequestState, Alert(), AlertAction(), AlertDescription(), AlertTitle(), alertVariants (+51 more)

### Community 11 - "codes_features_socle"
Cohesion: 0.10
Nodes (24): charger_bundle(), _distributions_reference(), empreinte_fichier(), ManifesteModele, Any, DataFrame, Path, Bundle versionné et vérifié du modèle SOCLE. (+16 more)

### Community 12 - "RefreshFields.tsx"
Cohesion: 0.10
Nodes (28): DecisionsTable(), DecisionsTableProps, LoanFields(), LoanFieldsProps, OBJETS, RefreshFields(), RefreshFieldsProps, DecisionRegistreVue (+20 more)

### Community 13 - "solida_modelisation/features.py"
Cohesion: 0.11
Nodes (31): construire_cible(), DataFrame, Timestamp, Construction déterministe de la cible de défaut à 30 jours., Retourne les quatre classes, sans lire les issues synthétiques du crédit., construire_jeu_socle(), ecrire_jeu_socle(), _features_epargne() (+23 more)

### Community 14 - "Monitoring sécurité — applicatif et infrastructure"
Cohesion: 0.25
Nodes (7): Ancrage réglementaire, Ce qui est explicitement laissé de côté (et pourquoi), Ce qui est surveillé aujourd'hui, Comptes bloqués — visibilité admin, Détection d'un volume de lecture hors norme, Intégrité du journal d'audit, Monitoring sécurité — applicatif et infrastructure

### Community 15 - "FeaturesSolidaires"
Cohesion: 0.19
Nodes (8): FeatureStore, date, Protocol, Simplification assumée pour cette passe, sans pipeline batch : `ecrire_lot`…, FeaturesSolidaires, `None` pour un sociétaire hors segment de groupe., _FakeFeatureStore, date

### Community 16 - "test_scoring.py"
Cohesion: 0.17
Nodes (28): client_agent(), client_auditeur(), client_superviseur(), _demande(), fixture, TestClient, societaire_agence_agent(), societaire_autre_agence() (+20 more)

### Community 17 - "cli.py"
Cohesion: 0.15
Nodes (20): auditer_risque_fuite(), Any, DataFrame, Produit une preuve d'audit, sans dissimuler une performance anormalement élevée., _commit_git(), main(), Entrées de ligne de commande du module modelisation., ecrire_rapport_resultat() (+12 more)

### Community 18 - "compilerOptions"
Cohesion: 0.05
Nodes (46): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+38 more)

### Community 19 - "CoreSimReader"
Cohesion: 0.08
Nodes (15): CoreSimReader, CompteEpargne, Credit, date, Garantie, GroupeCaution, MouvementEpargne, ProduitCredit (+7 more)

### Community 20 - "ConfigurationGrille"
Cohesion: 0.11
Nodes (24): grille_to_schema(), ConfigurationGrille, ConfigurationGrille, NouvelleConfigurationGrille, ParametresGrille, ParametresProgressif, ParametresScorecard, BaseModel (+16 more)

### Community 21 - "routers/notifications.py"
Cohesion: 0.20
Nodes (17): DemandeSocietaireNotification, PageNotifications, BaseModel, ArchiverNotification, AssignerNotification, ListerNotifications, demande_societaire_repository(), archiver_notification() (+9 more)

### Community 22 - "ProbabiliteDefaut"
Cohesion: 0.11
Nodes (22): ConstantScoringModel, Décomposition heuristique, PAS un modèle appris. `predire()` renvoie une…, Substitut du modèle réel : renvoie une probabilité de défaut fixe. Ce n'est pas…, Adaptateur du bundle EBM SOCLE vers le port métier de scoring., GrilleInvalide, Les paramètres de la grille de décision sont incohérents., decider(), ParametresGrille (+14 more)

### Community 23 - "dependencies"
Cohesion: 0.07
Nodes (35): class-variance-authority, clsx, cmdk, framer-motion, dependencies, class-variance-authority, clsx, cmdk (+27 more)

### Community 24 - "test_lister_decisions.py"
Cohesion: 0.30
Nodes (8): ListerDecisions, _decision(), _FakeCoreSimReader, _FakeDecisionRepository, `DecisionRepository.lister` filtre par l'agence de l'AGENT (seule donnée…, _societaire(), test_decision_hors_agence_de_lagent_est_exclue_meme_si_le_depot_la_renvoie(), test_superviseur_sans_filtre_agence_voit_tout()

### Community 25 - "CentreNotifications.tsx"
Cohesion: 0.14
Nodes (24): CentreNotificationsProps, CreditHistoryTableProps, GroupMembersTableProps, Section(), SectionProps, SimulationTab(), SimulationTabProps, Badge() (+16 more)

### Community 26 - "process_societaire_demande.py"
Cohesion: 0.16
Nodes (15): _produit_id_depuis_segment(), ResultatDemandeSocietaire, NotificationSender, Protocol, Canal externe (email ou autre, à définir) — reporté par décision explicite.…, calculer_pre_verification(), PreVerification, test_accord_avec_montant_couvert_donne_peut_avancer() (+7 more)

### Community 27 - "ModeleSocle"
Cohesion: 0.12
Nodes (9): EBMScoringModel, Path, ValeurFeature, Charge le champion MLflow, puis un cache vérifié, puis le bundle DVC local., ModeleSocle, DataFrame, Path, Adaptateur pur autour d'un bundle EBM contrôlé. (+1 more)

### Community 28 - "test_registre_et_grille.py"
Cohesion: 0.29
Nodes (14): _connecte(), _payload_grille(), TestClient, test_doublon_version_grille_renvoie_409_puis_une_version_unique_reussit(), test_lecture_grille_autorisee_a_lagent(), test_lecture_grille_autorisee_au_superviseur(), test_marge_hors_bornes_est_rejetee(), test_modification_grille_refusee_a_lagent() (+6 more)

### Community 29 - "Connectivité faible et connecteur de données réel"
Cohesion: 0.05
Nodes (39): Après le pilote, Architecture de déploiement retenue, Ce que signifie « manque de connexion », Comportement retenu pendant une coupure d'agence, Connecteur de données réel, Connectivité faible et connecteur de données réel, Corrections à appliquer à la note de présentation, Critère de réussite national (+31 more)

### Community 30 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 31 - "User"
Cohesion: 0.11
Nodes (29): AccessTokenDatabase, User, get_strategy(), DatabaseStrategy, UUID, current_active_user(), Request, SQLAlchemyAccessTokenDatabase (+21 more)

### Community 32 - "CoreSimPostgresReader"
Cohesion: 0.05
Nodes (27): CoreSimPostgresReader, CompteEpargne, Credit, date, Engine, Garantie, GroupeCaution, MouvementEpargne (+19 more)

### Community 33 - "adapters.py"
Cohesion: 0.14
Nodes (27): audit_log(), _client_seaweedfs(), core_sim_reader(), decision_repository(), feature_store(), fiche_archivee_repository(), fiche_pdf_generator(), fiche_repository() (+19 more)

### Community 34 - "DecisionEnregistree"
Cohesion: 0.10
Nodes (22): datetime, Engine, Implémente `DecisionRepository` contre `decision_scoring` (schéma `solida`).…, SqlDecisionRepository, decomposition_from_json(), decomposition_to_json(), Any, Conversion entre les lignes SQL et les décisions du domaine. (+14 more)

### Community 35 - "entrainement.py"
Cohesion: 0.26
Nodes (20): ExplainableBoostingClassifier, types_ebm(), _calibrer_si_necessaire(), _comparer_ponderation(), _creer_ebm(), entrainer_reference_logistique(), entrainer_socle_ebm(), _fit_ebm() (+12 more)

### Community 36 - "Étapes"
Cohesion: 0.11
Nodes (18): 10. Scorecard et décomposition, 11. Contrôle de non-discrimination, 12. Promotion, 1. Chargement et instantané, 2. Définition de la cible, 3. Découpage temporel, 4. Construction des features à `date_reference`, 5. Contrôle des fuites (+10 more)

### Community 37 - "Montant"
Cohesion: 0.16
Nodes (23): calculer_plafond(), _modulation_risque(), ParametresProgressif, Borne le montant recommandé par le principe du crédit progressif.…, Réglage du crédit progressif — voir docs/formules/., calculer_trajectoire(), Palier indicatif au prochain cycle, à profil de risque inchangé — jamais une…, Montant (+15 more)

### Community 38 - "ProduitCredit"
Cohesion: 0.15
Nodes (11): PostgresProduitReader, Engine, ProduitCredit, Lit le catalogue CORE-SIM, distinct des plafonds de la grille SOLIDA., produit_to_schema(), ProduitCredit, ListerProduits, ProduitCredit (+3 more)

### Community 39 - "De la probabilité au score, et du score à la décision"
Cohesion: 0.12
Nodes (15): Au-delà du refus : conditions de réexamen actionnables, Calibration, Chaîne complète, Connexion à la grille : ce n'est pas un mécanisme séparé, De la probabilité au score, et du score à la décision, Décomposition exacte en points, Garde-fous, Grille de décision (+7 more)

### Community 40 - "PolitiqueCredit.tsx"
Cohesion: 0.14
Nodes (20): PolicyPreset, PolitiqueCredit(), PolitiqueCreditProps, PolicyParameters, useSavePolicy(), save(), Tabs(), TabsContent() (+12 more)

### Community 41 - "verifier_jeton"
Cohesion: 0.24
Nodes (12): _prenom(), Societaire, ResultatAuthentification, generer_jeton(), Jeton signé, sans état côté serveur (pas de table de session) : le contenu…, None si le jeton est absent, malformé, falsifié ou expiré., _signature(), verifier_jeton() (+4 more)

### Community 42 - "ModeCalcul"
Cohesion: 0.25
Nodes (19): ContexteCascade, determiner_mode(), ParametresCascade, Seuils d'éligibilité au mode enrichi. Ajustable par la coopérative., Applique les quatre conditions du mode enrichi, dans l'ordre de leur…, Ce qu'il faut savoir sur le groupe d'un sociétaire pour choisir le modèle. Le…, ResultatCascade, ModeCalcul (+11 more)

### Community 43 - "Composants tiers et logiciels libres"
Cohesion: 0.22
Nodes (8): Backend (développement, test, construction ; hors chemin d'exécution), Backend et API (exécution), Composants tiers et logiciels libres, Frontend (développement, construction, test ; hors chemin d'exécution), Frontend (exécution), Infrastructure, images Docker de base, Note sur la LGPL (psycopg et psycopg2-binary), Simulateur, générateur de données synthétiques (exécution)

### Community 44 - "demarrer.sh"
Cohesion: 0.32
Nodes (14): attendre_disponibilite(), banniere(), conclure(), configurer_env(), construire_images(), demarrer_services(), echouer(), etape() (+6 more)

### Community 45 - "pipeline.py"
Cohesion: 0.06
Nodes (40): main(), Pont DVC vers le générateur CORE-SIM existant, sans dupliquer sa logique., ajouter_mouvements_nantissement(), charger_config(), choc_a_date(), construire_echeancier_theorique(), construire_soldes_mensuels(), _dates_echeances() (+32 more)

### Community 46 - "parametrage.py"
Cohesion: 0.22
Nodes (11): LireGrilleActive, ModifierGrille, ConfigurationGrille, La validation des seuils (marge/LGD positives, multiplicateurs croissants) est…, lire_grille_active(), modifier_grille(), lire(), modifier() (+3 more)

### Community 47 - "._calculate"
Cohesion: 0.25
Nodes (11): Calcule le score sans l'enregistrer — l'agent doit encore confirm avant que…, Recalcule à l'identique (les features CORE-SIM peuvent avoir changé entre la…, ScorerDemande, lister_conditions_reexamen(), ParametresReexamen, Cibles utilisées pour transformer un refus en parcours d'éligibilité., Leviers concrets et vérifiables que le sociétaire peut activer. Le refus cesse…, Snapshot des leviers observables pour un dossier qui n'est pas un accord simple. (+3 more)

### Community 48 - "demarrer.ps1"
Cohesion: 0.30
Nodes (12): Build-Images(), Initialize-Donnees(), Invoke-Etape(), New-Secret(), Set-Configuration(), Show-Etape(), Show-Info(), Show-Ok() (+4 more)

### Community 49 - "Évaluation"
Cohesion: 0.13
Nodes (14): Analyse par segment, Calibration, Ce qui est présenté au jury, Contrôle de non-discrimination, Courbe de coût et impact financier (métrique de démonstration), Discrimination, Les quatre pièges d'évaluation à éviter (spécifique microfinance), Métriques opérationnelles (+6 more)

### Community 50 - "LoginForm.tsx"
Cohesion: 0.06
Nodes (41): CentreNotifications(), confirmer(), ecarter(), ChangePasswordForm(), onSubmit(), FicheActions(), handleArchive(), FicheActionsProps (+33 more)

### Community 51 - "test_societaires.py"
Cohesion: 0.24
Nodes (14): client_agent(), fixture, TestClient, societaire_agence_agent(), societaire_autre_agence(), test_dossier_dun_societaire_de_son_agence_est_accessible(), test_dossier_dun_societaire_dune_autre_agence_est_refuse(), test_dossier_introuvable_renvoie_404() (+6 more)

### Community 52 - "Décisions provisoires à revoir"
Cohesion: 0.13
Nodes (14): Ajustement du générateur CORE-SIM, Approximations de l'adaptateur CORE-SIM, Auto-contrôle multi-octroi (pentest round 3, finding 12), Blocage connu : `next build` (image `front` de production), Décisions provisoires à revoir, Immutabilité des paramètres scorecard via l'API (pentest round 3, finding 9), Le modèle lui-même, `ModeleConstant.contributions()` : décomposition factice, PAS apprise (+6 more)

### Community 53 - "core_sim.py"
Cohesion: 0.14
Nodes (11): ListerSocietairesRecents, SocietaireSearchResult, Réutilise le journal d'audit plutôt qu'une table de récents dédiée., SocietaireSearchResult, RechercherSocietaire, AuditLog, Protocol, Chaque entrée : acteur, action, objet, horodatage. Jamais de mot de passe,… (+3 more)

### Community 54 - "_decomposition_to_schema"
Cohesion: 0.07
Nodes (44): _Definition, explication(), famille(), formater_valeur(), libelle(), Traduction des codes de variables du modèle vers ce qu'un agent doit lire à…, sens(), _decomposition_to_schema() (+36 more)

### Community 55 - "scorer_demande.py"
Cohesion: 0.26
Nodes (17): _actualiser_features(), _features_to_dict(), Calcule les ratios de la demande actuelle sans ajouter de charge externe. Les…, Préserve catégories et absences : EBM les interprète nativement., _revenu_effectif(), ActualisationSituation, DemandeScoring, FeaturesIndividuelles (+9 more)

### Community 56 - "frontend-societaire/components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 57 - "Formule cible du crédit progressif — à activer quand le modèle EBM réel existe"
Cohesion: 0.12
Nodes (16): 10. Corrections apportées — résumé, 1. Formule maîtresse, 2. L'ancre de capacité prouvée ($M$), 3. Le taux de variation lissé ($\delta_N$), 4. Les garde-fous, 5. Amorçage — premier prêt ($N=1$, pas d'historique), 6. Projection au prochain cycle — remplace `calculer_trajectoire`, 7. Paramètres — aucun n'est calibré, tous à trancher par rétro-test (+8 more)

### Community 58 - "Sélection de variables et prétraitement — principes"
Cohesion: 0.15
Nodes (12): Ce qu'on n'utilise pas, et pourquoi (choix assumé, défendable devant le jury), Contraintes de monotonie (optionnel, P2), La redondance survit, même sans VIF, Les interactions : EBM les trouve, on ne les fabrique pas à la main, Mais les variables construites restent le cœur : EBM ne les invente pas, Méthode de sélection retenue : l'importance native d'EBM, Protection métier et réglementaire, Périmètre hackathon (+4 more)

### Community 59 - "_row_to_credit"
Cohesion: 0.27
Nodes (7): _capital_restant_du(), PostgresCreditReader, Any, date, Engine, Approxime le capital restant dû. CORE-SIM ne fournit pas d'échéancier : la…, _row_to_credit()

### Community 60 - "env.py"
Cohesion: 0.24
Nodes (8): run_migrations_offline(), run_migrations_online(), url_migration(), configure_logging(), JSONFormatter, Journalisation applicative sur stdout, en JSON structuré — capturée par `docker…, Une ligne JSON par entrée, horodatée en UTC explicite — format standard pour…, LogRecord

### Community 61 - "MouvementEpargne"
Cohesion: 0.46
Nodes (6): MouvementEpargne, _mouvement(), date, MouvementEpargne, test_epargne_rejouee_exclut_mois_courant_et_futur(), test_restitution_nantie_ne_compte_pas_comme_depot_regulier()

### Community 62 - "connexion/page.tsx"
Cohesion: 0.32
Nodes (4): LogoAnime(), CHEMINS, PARTICULES, SavingsFlowBeam()

### Community 63 - "MLflow"
Cohesion: 0.17
Nodes (11): Artefacts, Ce qui est journalisé à chaque exécution, Configuration, Discipline, MLflow, Métriques, Organisation des expériences, Paramètres (+3 more)

### Community 64 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, start, test, typecheck

### Community 65 - "routers/produits.py"
Cohesion: 0.32
Nodes (5): ProduitCredit, BaseModel, lister(), get, ProduitCredit

### Community 66 - "metrics.py"
Cohesion: 0.20
Nodes (10): courbe_precision_rappel(), ecart_maximal_deciles(), erreur_calibration_attendue(), DataFrame, ndarray, Métriques de discrimination, calibration et recommandation., ECE pondérée en classes de probabilité de même largeur., Écart observé/prédit dans des déciles de population, pas de largeur fixe. (+2 more)

### Community 67 - "ScoringModel"
Cohesion: 0.20
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

### Community 89 - "DemandeSocietaire"
Cohesion: 0.13
Nodes (10): Any, NoopNotificationSender, Canal externe reporté (email ou autre, décision explicite) : log seulement,…, Engine, _row_to_demande(), SqlDemandeSocietaireRepository, DemandeSocietaireRepository, Protocol (+2 more)

### Community 91 - "Protocole obligatoire pour les agents (Claude Code, Codex)"
Cohesion: 0.20
Nodes (9): 1. Règle zéro : ne jamais inventer une décision, 2. Protocole de recherche obligatoire avant décision technique, 3. Périmètre et frontières, 4. Ordre de travail imposé, 5. Interdits absolus, 6. Style de production attendu, 7. Communication, 8. Rappel du contexte produit (+1 more)

### Community 121 - "plis_temporels_entrainement"
Cohesion: 0.24
Nodes (8): attribuer_split(), plis_temporels_entrainement(), DataFrame, ndarray, Series, Découpages temporels figés du SOCLE., Cinq plis expansifs, dont chaque validation est postérieure à son entraînement., test_decoupage_temporel_et_plis_croissants()

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

### Community 144 - "mensualite_actuarielle"
Cohesion: 0.38
Nodes (5): mensualite_actuarielle(), Calculs financiers partagés entre entraînement et inférence., Mensualité d'un prêt amortissable à échéances constantes, sans frais., test_mensualite_actuarielle_est_positive(), test_mensualite_actuarielle_taux_zero()

### Community 145 - "SOLIDA -- Generateur CORE-SIM v4"
Cohesion: 0.29
Nodes (6): Decisions terrain J1-05 a J1-13, Frontiere avec le modele, Produits et taux annuels, SOLIDA -- Generateur CORE-SIM v4, Sorties, Utilisation et validation

### Community 146 - "Rôles applicatifs vs organigramme réel (CEF-MF Lomé)"
Cohesion: 0.33
Nodes (5): Autres écarts notés, non urgents, Décision en attente : faut-il un rôle `chef_agence` ?, Rapprochement avec les 4 rôles actuels, Rôles applicatifs vs organigramme réel (CEF-MF Lomé), Écart principal : aucun rôle scopé à une seule agence en supervision

### Community 147 - "SqlFicheArchiveeRepository"
Cohesion: 0.33
Nodes (3): Engine, Implémente `FicheArchiveeRepository` contre `fiche_archivee` (schéma `solida`)., SqlFicheArchiveeRepository

### Community 148 - "Persistance et migrations"
Cohesion: 0.33
Nodes (5): Authentification : tables FastAPI-Users renommées, `decision_scoring` : garde-fou en base, pas seulement applicatif, Grille et progressif : paramétrables en base, pas dans le code, Persistance et migrations, Schéma `solida` (Alembic, migration initiale)

### Community 149 - "Journal de discussion conservé pour reprise"
Cohesion: 0.33
Nodes (5): Générateur J1-05 à J1-13, Journal de discussion conservé pour reprise, Provenance, SOCLE EBM J1-14 à J1-21, Suite demandée

### Community 150 - "Hooks Git et CI"
Cohesion: 0.33
Nodes (5): Activation (une fois par clone), Ce qui manque volontairement, CI, Hooks, Hooks Git et CI

### Community 151 - "orm_models/__init__.py"
Cohesion: 0.32
Nodes (8): AuditEvent, Base, DecisionScoring, FicheArchivee, Métadonnées seulement — le PDF lui-même vit dans le stockage objet (SeaweedFS),…, GrilleDecision, ModelVersion, DeclarativeBase

### Community 152 - "mappers/__init__.py"
Cohesion: 0.47
Nodes (3): Conversion des value objects du domaine vers les schémas pydantic exposés en…, demande_to_notification(), DemandeSocietaireAffichee

### Community 153 - "Scaffold backend et outillage Python"
Cohesion: 0.40
Nodes (4): Arborescence, Docker, Outillage (uv, ruff, mypy, pytest, import-linter), Scaffold backend et outillage Python

### Community 154 - "Adaptateur CORE-SIM"
Cohesion: 0.40
Nodes (4): Adaptateur CORE-SIM, Agrégats de groupe : toujours du point de vue du sociétaire consulté, Colonnes absentes du générateur, estimées à l'affichage, Variables jamais lues

### Community 155 - "Constat Claude — plafonds par produit"
Cohesion: 0.40
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

### Community 163 - "prettier"
Cohesion: 0.67
Nodes (3): prettier, prettier, prettier

### Community 164 - "shadcn"
Cohesion: 0.67
Nodes (3): shadcn, shadcn, shadcn

### Community 168 - "errors.py"
Cohesion: 0.15
Nodes (22): DomainError, DonneesInsuffisantes, IdentiteSocietaireInvalide, ModeleIndisponible, MotDePasseInvalide, Les données disponibles ne permettent pas de calculer un score., Racine commune à toutes les exceptions du domaine SOLIDA., Aucun modèle de scoring (ni enrichi, ni socle) n'a pu produire une probabilité. (+14 more)

### Community 170 - "Authentification"
Cohesion: 0.25
Nodes (7): Authentification, Endpoints, FastAPI-Users, session révocable unique, Politique de mot de passe, Provisioning et cycle de vie des comptes, Rôles et cloisonnement, Simplification à noter

### Community 174 - "Convention de nommage technique (refactor SOLID / anglicisation)"
Cohesion: 0.25
Nodes (7): Adaptateurs concrets, Autres décisions, Ce qui ne change pas, Convention de nommage technique (refactor SOLID / anglicisation), Décision, Ports (`domain/ports/`), Routeurs et authentification

### Community 187 - "RecommendationPanel.tsx"
Cohesion: 0.15
Nodes (20): ContributionsChart(), FactorsPanel(), FactorsPanelProps, NumberTicker(), RecommendationPanel(), RecommendationPanelProps, ScoringResultView(), ScoringResultViewProps (+12 more)

### Community 189 - "post-commit"
Cohesion: 0.40
Nodes (4): post-commit script, GRAPHIFY_CHANGED, GRAPHIFY_REBUILD_LOG, PYTHONHASHSEED

### Community 193 - "frontend-societaire/package.json"
Cohesion: 0.13
Nodes (14): engines, node, name, overrides, @vitest/mocker, private, scripts, build (+6 more)

### Community 195 - "test_executer_compose_le_dossier_complet"
Cohesion: 0.23
Nodes (11): _credit(), _FakeCoreSimReader, _groupe(), _membre(), CompteEpargne, date, GroupeCaution, MouvementEpargne (+3 more)

### Community 197 - "devDependencies"
Cohesion: 0.07
Nodes (36): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, husky, lint-staged, tailwindcss (+28 more)

### Community 201 - "routers/scoring.py"
Cohesion: 0.15
Nodes (19): ArchiverFiche, GenererFiche, FicheRepository, Protocol, Stockage objet des fiches PDF archivées — jamais en base (`solida` reste léger)., FicheArchiveeRepository, Protocol, Métadonnées de l'archivage (le PDF lui-même est dans `FicheRepository`). (+11 more)

### Community 226 - "routers/societaires.py"
Cohesion: 0.13
Nodes (19): ConsulterDossier, AccesRefuse, L'acteur courant n'a pas les droits nécessaires pour cette action., create_application(), consulter_dossier(), get, read_health(), _agence_agent() (+11 more)

### Community 228 - "post-checkout"
Cohesion: 0.50
Nodes (3): post-checkout script, GRAPHIFY_REBUILD_LOG, PYTHONHASHSEED

### Community 248 - "routers/auth.py"
Cohesion: 0.10
Nodes (31): datetime, Engine, Renvoie les objets distincts récents pour alimenter les sociétaires récents., Implémente `AuditLog` contre `journal_audit` (schéma `solida`)., SqlAuditLog, AccessToken, client_ip_address(), Request (+23 more)

### Community 269 - "routers/portail.py"
Cohesion: 0.16
Nodes (21): DemandePreVerificationReponse, DemandePreVerificationRequete, BaseModel, VerificationCompteReponse, VerificationCompteRequete, AuthenticateSocietaire, ProcessSocietaireDemande, notification_sender() (+13 more)

### Community 287 - "ThresholdsTab.tsx"
Cohesion: 0.13
Nodes (16): ibmPlexMono, ibmPlexSans, sourceSerif4, metadata, PolicyPreset, ThresholdsTab(), ThresholdsTabProps, Separator() (+8 more)

## Knowledge Gaps
- **507 isolated node(s):** `CHOIX`, `metadata`, `viewport`, `REPERES`, `$schema` (+502 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_membre()` connect `test_executer_compose_le_dossier_complet` to `CentreNotifications.tsx`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `MembreGroupe` connect `CentreNotifications.tsx` to `frontend/lib/contracts.ts`, `test_executer_compose_le_dossier_complet`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `MouvementEpargne` connect `MouvementEpargne` to `CoreSimPostgresReader`, `test_consulter_dossier_mapping.py`, `test_executer_compose_le_dossier_complet`, `feature_store_core_sim.py`, `CoreSimReader`, `core_sim.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ProbabiliteDefaut` (e.g. with `ConstantScoringModel` and `EBMScoringModel`) actually correct?**
  _`ProbabiliteDefaut` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Montant` (e.g. with `ScorerDemande` and `ParametresProgressif`) actually correct?**
  _`Montant` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `CoreSimReader` (e.g. with `FeatureStoreCoreSim` and `AuthenticateSocietaire`) actually correct?**
  _`CoreSimReader` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CHOIX`, `metadata`, `viewport` to the rest of the system?**
  _507 weakly-connected nodes found - possible documentation gaps or missing edges._