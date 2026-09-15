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
  refus: "REFUS",
  // Historique uniquement : plus jamais produite depuis le passage à 3 tranches, mais une
  // décision archivée peut encore la porter (voir TrancheDecision.COMITE_DE_CREDIT, backend).
  comite_de_credit: "COMITÉ DE CRÉDIT",
};

/**
 * Ce que chaque tranche signifie concrètement, à afficher à côté du résultat brut
 * (`RecommendationPanel.tsx`) pour qu'une décision ne soit jamais qu'un mot et un score.
 * Le passage en comité de crédit n'est JAMAIS optionnel, quelle que soit la tranche — c'est la
 * mention légale de toute fiche (`03-MODELE/11-formule-cible-credit-progressif.md:77-80` :
 * « La décision finale relève de l'agent de crédit et du comité de crédit de la coopérative »).
 * Ces textes ne varient donc que sur ce que le signal du modèle indique, jamais sur la
 * nécessité du comité.
 */
export const EXPLICATION_TRANCHE: Record<Tranche, string> = {
  accord:
    "Le modèle ne détecte pas de signal de risque notable sur ce profil : la recommandation " +
    "est favorable. Comme pour tout dossier, la décision finale relève de l'agent et du comité " +
    "de crédit.",
  accord_sous_condition:
    "La recommandation est favorable, sous réserve du point signalé ci-dessous (conditions de " +
    "réexamen) à porter devant le comité de crédit, qui statuera avec l'agent.",
  refus:
    "Le profil de risque est trop élevé pour une recommandation favorable en l'état. Ce n'est " +
    "pas automatique ni définitif : le comité de crédit peut réexaminer le dossier à la lumière " +
    "des conditions listées ci-dessous.",
  // Historique uniquement (voir LABEL_TRANCHE ci-dessus) : texte conservé tel qu'affiché à
  // l'époque pour une décision archivée sous cette tranche, jamais montré pour une nouvelle.
  comite_de_credit:
    "Le signal du modèle était incertain sur ce dossier : il appelait un examen approfondi en " +
    "comité de crédit avant toute décision.",
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
    refus: {
      text: "text-decision-refus",
      background: "bg-decision-refus-fond",
      border: "border-l-decision-refus",
    },
    // Historique uniquement (voir LABEL_TRANCHE ci-dessus).
    comite_de_credit: {
      text: "text-decision-comite",
      background: "bg-decision-comite-fond",
      border: "border-l-decision-comite",
    },
  };
