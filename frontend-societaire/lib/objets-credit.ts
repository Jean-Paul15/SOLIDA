import type { LucideIcon } from "lucide-react";
import {
  Wheat,
  Package,
  Wrench,
  HeartPulse,
  GraduationCap,
  Home,
  HelpCircle,
} from "lucide-react";

export type ObjetCredit =
  | "fonds_roulement"
  | "stock"
  | "intrants_agricoles"
  | "equipement"
  | "urgence_sante"
  | "scolarite"
  | "habitat"
  | "autre";

export type Divisibilite = "divisible" | "indivisible" | "mixte";

interface DefinitionObjet {
  libelle: string;
  icone: LucideIcon;
  divisibilite: Divisibilite;
}

/**
 * Table de correspondance objet -> divisibilité, section 1.7 de
 * SOLIDA_Complements_et_Strategie.md (référencée nommément par
 * SOLIDA_Flux_Societaire.md section 4). Cette table couvre explicitement
 * fonds_de_roulement/achat_stock/campagne_agricole (divisible) et
 * achat_moto/achat_tricycle/achat_equipement/achat_machine (indivisible),
 * amenagement_local/construction (mixte) — un vocabulaire de crédit "typé agent".
 *
 * Le champ objet_credit réellement généré par CORE-SIM (PLAN 72H/
 * SOLIDA_Schema_Donnees_a_valider.md section 6.1) est plus large et ne recouvre pas
 * ce vocabulaire mot pour mot. Correspondance retenue ici, en l'absence d'arbitrage
 * explicite sur ce point précis :
 * - fonds_roulement -> fonds_de_roulement (divisible, correspondance directe)
 * - stock -> achat_stock (divisible, correspondance directe)
 * - intrants_agricoles -> campagne_agricole (divisible, même nature : intrants
 *   consommables pour une campagne, achetables en quantité réduite)
 * - equipement -> achat_equipement (indivisible, correspondance directe)
 * - urgence_sante, scolarite, habitat, autre : absents de la table 1.7. Traités en
 *   "mixte" par défaut, conformément à la règle explicite du document pour tout ce
 *   qui échappe à la liste ("cas prudent à vérifier manuellement, jamais deviné") —
 *   PAS une divisibilité devinée. À faire trancher explicitement si ces quatre
 *   objets doivent rejoindre le catalogue 1.7 avec leur propre statut.
 */
export const OBJETS_CREDIT: Record<ObjetCredit, DefinitionObjet> = {
  fonds_roulement: { libelle: "Fonds de roulement", icone: Wheat, divisibilite: "divisible" },
  stock: { libelle: "Achat de stock", icone: Package, divisibilite: "divisible" },
  intrants_agricoles: {
    libelle: "Campagne agricole",
    icone: Wheat,
    divisibilite: "divisible",
  },
  equipement: { libelle: "Équipement ou machine", icone: Wrench, divisibilite: "indivisible" },
  urgence_sante: { libelle: "Urgence de santé", icone: HeartPulse, divisibilite: "mixte" },
  scolarite: { libelle: "Scolarité", icone: GraduationCap, divisibilite: "mixte" },
  habitat: { libelle: "Habitat", icone: Home, divisibilite: "mixte" },
  autre: { libelle: "Autre", icone: HelpCircle, divisibilite: "mixte" },
};

export const LISTE_OBJETS_CREDIT = Object.keys(OBJETS_CREDIT) as ObjetCredit[];
