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

export type ModeCalcul = "socle_seul" | "enrichi";

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

export interface EntreeScoring {
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

export interface ResultatScoring {
  decision_id: string;
  score: number;
  tranche: Tranche;
  montant_recommande: number;
  montant_demande: number;
  mode_calcul: ModeCalcul;
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
  resultat: ResultatScoring;
  demande: EntreeScoring;
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

export interface ResultatRechercheSocietaire {
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

export interface PointSolde {
  mois: string;
  solde: number;
}

export interface SyntheseEpargne {
  solde_moyen_6m: number;
  tendance_12m: TendanceEpargne;
  nb_mois_avec_depot_12m: number;
  volatilite: number;
  ratio_epargne_revenu: number;
  anciennete_relation_mois: number;
  serie_solde_12m: PointSolde[];
}

export interface CreditResume {
  credit_id: string;
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

export interface ErreurApi {
  code: string;
  message: string;
  details?: unknown;
}
