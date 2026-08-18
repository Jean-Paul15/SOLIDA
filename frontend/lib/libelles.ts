import type { ObjetCredit, StatutCredit, Tranche } from "@/lib/contracts";

export const LIBELLE_OBJET_CREDIT: Record<ObjetCredit, string> = {
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
export const LIBELLE_STATUT_CREDIT: Record<StatutCredit, string> = {
  en_cours: "En cours",
  solde: "Solde",
  en_souffrance: "En souffrance",
  radie: "Radié",
  restructure: "Restructuré",
};

/** Statut d'un membre de groupe de caution (`MembreGroupe.statut_credit`) : ensemble de
 * valeurs distinct de `StatutCredit` (inclut "aucun_credit", exclut "radie"/"restructure"). */
export const LIBELLE_STATUT_CREDIT_MEMBRE: Record<
  "aucun_credit" | "en_cours" | "solde" | "en_souffrance",
  string
> = {
  aucun_credit: "Aucun crédit",
  en_cours: "En cours",
  solde: "Soldé",
  en_souffrance: "En souffrance",
};

export const LIBELLE_TRANCHE: Record<Tranche, string> = {
  accord: "ACCORD",
  accord_sous_condition: "ACCORD SOUS CONDITION",
  comite_de_credit: "COMITÉ DE CRÉDIT",
  refus: "REFUS",
};

export const COULEUR_TRANCHE: Record<Tranche, { texte: string; fond: string; bordure: string }> = {
  accord: {
    texte: "text-decision-accord",
    fond: "bg-decision-accord-fond",
    bordure: "border-l-decision-accord",
  },
  accord_sous_condition: {
    texte: "text-decision-conditionnel",
    fond: "bg-decision-conditionnel-fond",
    bordure: "border-l-decision-conditionnel",
  },
  comite_de_credit: {
    texte: "text-decision-comite",
    fond: "bg-decision-comite-fond",
    bordure: "border-l-decision-comite",
  },
  refus: {
    texte: "text-decision-refus",
    fond: "bg-decision-refus-fond",
    bordure: "border-l-decision-refus",
  },
};
