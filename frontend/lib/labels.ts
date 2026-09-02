import type { ObjetCredit, RoleGroupe, StatutCredit, Tranche } from "@/lib/contracts";

export const LABEL_OBJET_CREDIT: Record<ObjetCredit, string> = {
  fonds_roulement: "Fonds de roulement",
  equipement: "Équipement",
  intrants_agricoles: "Intrants agricoles",
  stock: "Stock",
  urgence_sante: "Urgence santé",
  scolarite: "Scolarité",
  habitat: "Habitat",
  autre: "Autre",
};

/** Statut d'un crédit dans l'historique propre d'un sociétaire (`CreditResume.statut`). */
export const LABEL_STATUT_CREDIT: Record<StatutCredit, string> = {
  en_cours: "En cours",
  solde: "Solde",
  en_souffrance: "En souffrance",
  radie: "Radié",
  restructure: "Restructuré",
};

/** Statut d'un membre de groupe de caution (`MembreGroupe.statut_credit`) : ensemble de
 * valeurs distinct de `StatutCredit` (inclut "aucun_credit", exclut "radie"/"restructure"). */
export const LABEL_STATUT_CREDIT_MEMBRE: Record<
  "aucun_credit" | "en_cours" | "solde" | "en_souffrance",
  string
> = {
  aucun_credit: "Aucun crédit",
  en_cours: "En cours",
  solde: "Soldé",
  en_souffrance: "En souffrance",
};

export const GROUP_ROLE_LABEL: Record<RoleGroupe, string> = {
  membre: "Membre",
  presidente: "Présidente",
  tresoriere: "Trésorière",
  secretaire: "Secrétaire",
};

export const LABEL_TRANCHE: Record<Tranche, string> = {
  accord: "ACCORD",
  accord_sous_condition: "ACCORD SOUS CONDITION",
  comite_de_credit: "COMITÉ DE CRÉDIT",
  refus: "REFUS",
};

export const TRANCHE_COLOR: Record<Tranche, { text: string; background: string; border: string }> =
  {
    accord: {
      text: "text-decision-accord",
      background: "bg-decision-accord-fond",
      border: "border-l-decision-accord",
    },
    accord_sous_condition: {
      text: "text-decision-conditionnel",
      background: "bg-decision-conditionnel-fond",
      border: "border-l-decision-conditionnel",
    },
    comite_de_credit: {
      text: "text-decision-comite",
      background: "bg-decision-comite-fond",
      border: "border-l-decision-comite",
    },
    refus: {
      text: "text-decision-refus",
      background: "bg-decision-refus-fond",
      border: "border-l-decision-refus",
    },
  };
