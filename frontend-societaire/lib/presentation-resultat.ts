import type { DemandePreVerificationReponse, IssuePreVerification } from "./contracts";

export interface PresentationResultat {
  montantRecommande: number | undefined;
  /** Classes Tailwind : mêmes tokens décision-* que le frontend agent
   * (lib/labels.ts), pour une lecture visuelle cohérente entre les deux sites. */
  styleAmbiance: string;
}

const STYLE_PAR_ISSUE: Record<IssuePreVerification, string> = {
  peut_avancer: "border-decision-accord/30 bg-decision-accord-fond",
  montant_reduit: "border-decision-conditionnel/30 bg-decision-conditionnel-fond",
  duree_ou_attente: "border-decision-comite/30 bg-decision-comite-fond",
  pas_maintenant: "border-decision-refus/30 bg-decision-refus-fond",
};

export function presentationResultat(
  resultat: DemandePreVerificationReponse
): PresentationResultat {
  return {
    montantRecommande: resultat.issue === "montant_reduit" ? resultat.montant_propose : undefined,
    styleAmbiance: STYLE_PAR_ISSUE[resultat.issue],
  };
}
