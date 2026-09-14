import { describe, expect, it } from "vitest";
import { presentationResultat } from "./presentation-resultat";
import type { DemandePreVerificationReponse } from "./contracts";

function reponse(
  partielle: Partial<DemandePreVerificationReponse>
): DemandePreVerificationReponse {
  return { issue: "peut_avancer", message: "", demande_id: "demande-1", ...partielle };
}

describe("presentationResultat", () => {
  it("expose le montant proposé uniquement pour l'issue montant_reduit", () => {
    const { montantRecommande } = presentationResultat(
      reponse({ issue: "montant_reduit", montant_propose: 150_000 })
    );
    expect(montantRecommande).toBe(150_000);
  });

  it("ne propose jamais de montant réduit sur les autres issues", () => {
    for (const issue of ["peut_avancer", "duree_ou_attente", "pas_maintenant"] as const) {
      const { montantRecommande } = presentationResultat(
        reponse({ issue, montant_propose: 150_000 })
      );
      expect(montantRecommande).toBeUndefined();
    }
  });
});
