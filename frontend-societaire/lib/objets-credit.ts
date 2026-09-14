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

interface DefinitionObjet {
  libelle: string;
  icone: LucideIcon;
}

/** Libellés alignés sur frontend/lib/labels.ts (LABEL_OBJET_CREDIT) : un même objet de crédit
 * doit se nommer pareil aux yeux de l'agent et du sociétaire. */
export const OBJETS_CREDIT: Record<ObjetCredit, DefinitionObjet> = {
  fonds_roulement: { libelle: "Fonds de roulement", icone: Wheat },
  stock: { libelle: "Stock", icone: Package },
  intrants_agricoles: { libelle: "Intrants agricoles", icone: Wheat },
  equipement: { libelle: "Équipement", icone: Wrench },
  urgence_sante: { libelle: "Urgence santé", icone: HeartPulse },
  scolarite: { libelle: "Scolarité", icone: GraduationCap },
  habitat: { libelle: "Habitat", icone: Home },
  autre: { libelle: "Autre", icone: HelpCircle },
};

export const LISTE_OBJETS_CREDIT = Object.keys(OBJETS_CREDIT) as ObjetCredit[];
