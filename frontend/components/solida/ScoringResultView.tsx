"use client";

import { useMemo } from "react";
import { FactorsPanel } from "@/components/solida/FactorsPanel";
import { RecommendationPanel } from "@/components/solida/RecommendationPanel";
import { useConfigurationGrille } from "@/components/solida/useConfigurationGrille";
import type { ScoringResult } from "@/lib/contracts";
import { zoneBounds } from "@/lib/score-gauge";

interface ScoringResultViewProps {
  result: ScoringResult;
  /** Aperçu non encore enregistré : bascule les actions vers confirmer/annuler plutôt
   * que d'afficher les actions d'une décision déjà persistée (fiche, "enregistrée le"). */
  isPreview?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmationInProgress?: boolean;
}

export function ScoringResultView({
  result,
  isPreview = false,
  onConfirm,
  onCancel,
  confirmationInProgress = false,
}: ScoringResultViewProps) {
  const configurationGrille = useConfigurationGrille();
  const zones = useMemo(
    () => (configurationGrille ? zoneBounds(configurationGrille) : null),
    [configurationGrille]
  );

  return (
    <div className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-6 px-6 py-6">
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-5">
          <RecommendationPanel result={result} zones={zones} />
        </div>
        <div className="col-span-7">
          <FactorsPanel
            result={result}
            isPreview={isPreview}
            onConfirm={onConfirm}
            onCancel={onCancel}
            confirmationInProgress={confirmationInProgress}
          />
        </div>
      </div>
    </div>
  );
}
