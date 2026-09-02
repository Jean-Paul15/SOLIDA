import { useState } from "react";
import { toast } from "sonner";
import type { ConfigurationGrilleApi } from "@/lib/contracts";
import { apiFetch, useApiErrorToast } from "@/lib/services/error-service";
import { withMinDuration } from "@/lib/timing";

interface PolicyParameters {
  margin: number;
  lgd: number;
  approvalMultiplier: number;
  reviewMultiplier: number;
  productCaps: Record<string, number>;
}

export function useSavePolicy(initialConfiguration: ConfigurationGrilleApi, canEdit: boolean) {
  const [version, setVersion] = useState(initialConfiguration.version_grille);
  const [isSaving, setIsSaving] = useState(false);
  const handleError = useApiErrorToast();

  async function save(parameters: PolicyParameters) {
    if (!canEdit) return;
    setIsSaving(true);
    // Une version héritée invalide repart d'un format affichable pour l'agent.
    const match = /^v(\d+)\.(\d+)$/.exec(version);
    const nextVersion = match ? `v${match[1]}.${Number(match[2]) + 1}` : "v1.0";
    const {
      pdo,
      score_reference: scoreReference,
      odds_reference: oddsReference,
    } = initialConfiguration.scorecard;
    try {
      await withMinDuration(
        apiFetch("/api/v1/parametrage/grille", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            version_grille: nextVersion,
            grille: {
              marge: parameters.margin,
              lgd: parameters.lgd,
              multiplicateur_accord: parameters.approvalMultiplier,
              multiplicateur_vigilance: initialConfiguration.grille.multiplicateur_vigilance,
              multiplicateur_examen: parameters.reviewMultiplier,
            },
            progressif: {
              ...initialConfiguration.progressif,
              plafonds_produits: parameters.productCaps,
            },
            scorecard: { pdo, score_reference: scoreReference, odds_reference: oddsReference },
          }),
        })
      );
      setVersion(nextVersion);
      toast.success(`Politique de crédit ${nextVersion} enregistrée`);
    } catch (e) {
      handleError(e, "L'enregistrement a échoué.");
    } finally {
      setIsSaving(false);
    }
  }

  return { version, isSaving, save };
}
