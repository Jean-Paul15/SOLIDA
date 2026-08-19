"use client";

import { useMemo } from "react";
import { PanneauFacteurs } from "@/components/solida/PanneauFacteurs";
import { PanneauRecommandation } from "@/components/solida/PanneauRecommandation";
import { useConfigurationGrille } from "@/components/solida/useConfigurationGrille";
import type { ScoringResult } from "@/lib/contracts";
import { bornesZones } from "@/lib/jauge-score";

interface ResultatScoringVueProps {
  resultat: ScoringResult;
  /** Aperçu non encore enregistré : bascule les actions vers confirmer/annuler plutôt
   * que d'afficher les actions d'une décision déjà persistée (fiche, "enregistrée le"). */
  previsualisation?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmationEnCours?: boolean;
}

export function ResultatScoringVue({
  resultat,
  previsualisation = false,
  onConfirm,
  onCancel,
  confirmationEnCours = false,
}: ResultatScoringVueProps) {
  const configurationGrille = useConfigurationGrille();
  const zones = useMemo(
    () => (configurationGrille ? bornesZones(configurationGrille) : null),
    [configurationGrille]
  );

  return (
    <div className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-6 px-6 py-6">
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-5">
          <PanneauRecommandation resultat={resultat} zones={zones} />
        </div>
        <div className="col-span-7">
          <PanneauFacteurs
            resultat={resultat}
            previsualisation={previsualisation}
            onConfirm={onConfirm}
            onCancel={onCancel}
            confirmationEnCours={confirmationEnCours}
          />
        </div>
      </div>
    </div>
  );
}
