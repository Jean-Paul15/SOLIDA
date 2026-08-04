import type { ObjetCredit, Tranche } from "@/lib/contracts";

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
