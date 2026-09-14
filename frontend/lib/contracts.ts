export type ObjetCredit =
  | "fonds_roulement"
  | "equipement"
  | "intrants_agricoles"
  | "stock"
  | "urgence_sante"
  | "scolarite"
  | "habitat"
  | "autre";

export type Segment = "salarie" | "individuel" | "jeune" | "femme_gie" | "agricole";

export type StatutSocietaire = "actif" | "inactif" | "radie";

export type Tranche = "accord" | "accord_sous_condition" | "comite_de_credit" | "refus";

export type CalculationMode = "socle_seul" | "enrichi";

export type TendanceEpargne = "hausse" | "stable" | "erosion";

export type StatutCredit = "en_cours" | "solde" | "en_souffrance" | "radie" | "restructure";

export type StatutGroupe = "actif" | "dissous" | "en_difficulte";

export type RoleGroupe = "membre" | "presidente" | "tresoriere" | "secretaire";

export type SensContribution = "favorable" | "defavorable" | "neutre";

export type FamilleContribution =
  "profil" | "activite" | "epargne" | "historique" | "solidaire" | "demande";

export interface ActualisationSituation {
  revenu_mensuel_declare?: number;
  charges_mensuelles?: number;
  nb_personnes_a_charge?: number;
}

export interface ScoringInput {
  societaire_id: string;
  produit_id: string;
  montant_demande: number;
  duree_demandee_mois: number;
  objet_credit: ObjetCredit;
  groupe_id?: string;
  actualisation?: ActualisationSituation;
}

export interface ContributionVariable {
  code_variable: string;
  libelle: string;
  valeur: string;
  points: number;
  sens: SensContribution;
  famille: FamilleContribution;
  explication: string;
}

export interface PalierProgression {
  cycle: number;
  plafond_accessible: number;
}

export interface ScoringResult {
  decision_id: string;
  societaire_id: string;
  score: number;
  tranche: Tranche;
  montant_recommande: number;
  montant_demande: number;
  mode_calcul: CalculationMode;
  motif_mode?: string;
  decomposition: ContributionVariable[];
  points_de_base: number;
  plafond_progressif: number;
  trajectoire_progression: PalierProgression[];
  conditions_reexamen: string[];
  version_modele: string;
  version_grille: string;
  horodatage: string;
  avertissements: string[];
}

export interface FicheJustification {
  fiche_id: string;
  resultat: ScoringResult;
  demande: ScoringInput;
  societaire_nom: string;
  numero_membre: string;
  agence: string;
  agent_nom: string;
  date_edition: string;
  facteurs_favorables: ContributionVariable[];
  facteurs_defavorables: ContributionVariable[];
  conditions_reexamen: string[];
  mention_legale: string;
}

export interface SocietaireSearchResult {
  societaire_id: string;
  nom_complet: string;
  numero_membre: string;
  agence: string;
  zone: string;
  statut: StatutSocietaire;
  a_credit_en_cours: boolean;
}

export type NiveauInstruction = "aucun" | "primaire" | "secondaire" | "superieur";

export interface IdentiteSocietaire {
  societaire_id: string;
  numero_membre: string;
  nom_complet: string;
  segment: Segment;
  agence: string;
  date_adhesion: string;
  anciennete_mois: number;
  statut: StatutSocietaire;
  age: number;
  niveau_instruction?: NiveauInstruction;
}

export interface ActiviteEconomique {
  secteur: string;
  anciennete_activite_mois: number;
  revenu_mensuel_declare?: number;
  charges_mensuelles?: number;
  capacite_remboursement_estimee: number;
  nb_personnes_a_charge: number;
  parts_sociales_montant: number;
}

export type SensMouvementEpargne = "depot" | "retrait";

export interface MouvementEpargne {
  date_operation: string;
  sens: SensMouvementEpargne;
  montant: number;
}

export interface SyntheseEpargne {
  solde_moyen_6m: number;
  tendance_12m: TendanceEpargne;
  nb_mois_avec_depot_12m: number;
  volatilite: number;
  ratio_epargne_revenu: number;
  anciennete_relation_mois: number;
  mouvements_recents: MouvementEpargne[];
}

export interface CreditResume {
  credit_id: string;
  produit_id: string;
  date_deblocage: string;
  montant_octroye: number;
  duree_mois: number;
  numero_cycle: number;
  statut: StatutCredit;
  capital_restant_du: number;
  max_jours_retard: number;
}

export interface MembreGroupe {
  societaire_id: string;
  nom_complet: string;
  role: RoleGroupe;
  anciennete_mois: number;
  statut_credit: "aucun_credit" | "en_cours" | "solde" | "en_souffrance";
  caution_appelee: boolean;
}

export interface SyntheseGroupe {
  groupe_id: string;
  nom_groupe: string;
  taille_actuelle: number;
  date_creation: string;
  taux_remboursement_groupe: number | null;
  nb_cycles_completes: number;
  nb_sorties_12m: number;
  statut: StatutGroupe;
  membres: MembreGroupe[];
}

export interface DossierSocietaire {
  identite: IdentiteSocietaire;
  activite: ActiviteEconomique;
  epargne: SyntheseEpargne;
  historique_credit: CreditResume[];
  groupe?: SyntheseGroupe;
  alertes: string[];
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: unknown;
}

export interface DecisionRegistreApi {
  decision_id: string;
  societaire_id: string;
  societaire_nom: string;
  agence: string;
  demande: ScoringInput;
  resultat: ScoringResult;
  horodatage: string;
  agent_nom: string;
}

export interface DemandeSocietaireApi {
  demande_id: string;
  societaire_id: string;
  societaire_nom: string;
  agence_id: string;
  montant_demande: number;
  objet_credit: ObjetCredit;
  duree_mois: number;
  produit_id: string;
  resultat: ScoringResult;
  statut: string;
  cree_le: string;
  assigne_a_agent_id: string | null;
}

export interface PageNotificationsApi {
  elements: DemandeSocietaireApi[];
  total: number;
}

export interface GridParametersApi {
  marge: number;
  lgd: number;
  multiplicateur_accord: number;
  multiplicateur_vigilance: number;
  multiplicateur_examen: number;
}

export interface ProgressiveParametersApi {
  coefficient_progression: number;
  montant_plancher: number;
  plafonds_produits: Record<string, number>;
  plafond_primo_emprunteur: number;
  modulation_base: number;
  modulation_pente: number;
  modulation_min: number;
  modulation_max: number;
}

export interface ProduitCreditApi {
  produit_id: string;
  libelle: string;
  type_garantie: string;
  montant_min: number;
  montant_max: number;
  duree_min_mois: number;
  duree_max_mois: number;
  taux_annuel: number;
}

export interface ScorecardParametersApi {
  pdo: number;
  score_reference: number;
  odds_reference: number;
}

export interface ConfigurationGrilleApi {
  version_grille: string;
  grille: GridParametersApi;
  progressif: ProgressiveParametersApi;
  scorecard: ScorecardParametersApi;
  auteur: string;
  date_activation: string;
  active: boolean;
}

export interface LoginResponseApi {
  name: string;
  role: string;
  agence: string | null;
  must_change_password: boolean;
}
