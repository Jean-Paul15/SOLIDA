"use client";

import { useMemo, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ThresholdsTab } from "@/components/solida/ThresholdsTab";
import { SimulationTab } from "@/components/solida/SimulationTab";
import { useSavePolicy } from "@/components/solida/useSavePolicy";
import type { ConfigurationGrilleApi } from "@/lib/contracts";
import { canEditGrille } from "@/lib/roles";
import { probabiliteDepuisScore, seuilEconomique, trancheDepuisProbabilite } from "@/lib/scorecard";

interface PolitiqueCreditProps {
  historicalScores: number[];
  initialConfiguration: ConfigurationGrilleApi;
  role: string | undefined;
}

type PolicyPreset = "prudent" | "equilibre" | "expansion";

export function PolitiqueCredit({
  historicalScores,
  initialConfiguration,
  role,
}: PolitiqueCreditProps) {
  const canEdit = canEditGrille(role);
  // PDO, score de référence et rapport de référence ne sont plus édités depuis cet écran
  // (administration du modèle hors périmètre SOLIDA) : ils sont retransmis inchangés à
  // l'enregistrement.
  const {
    pdo,
    score_reference: scoreReference,
    odds_reference: oddsReference,
  } = initialConfiguration.scorecard;
  const [margin, setMargin] = useState(initialConfiguration.grille.marge);
  const [lgd, setLgd] = useState(initialConfiguration.grille.lgd);
  const [approvalMultiplier, setApprovalMultiplier] = useState(
    initialConfiguration.grille.multiplicateur_accord
  );
  const [preset, setPreset] = useState<PolicyPreset>("equilibre");

  const scorecardParameters = { pdo, scoreReference, oddsReference };
  const gridParameters = {
    marge: margin,
    lgd,
    multiplicateurAccord: approvalMultiplier,
  };
  const threshold = seuilEconomique(gridParameters);

  const { isSaving, save } = useSavePolicy(initialConfiguration, canEdit);

  const distribution = useMemo(() => {
    const counts: Record<string, number> = {
      accord: 0,
      accord_sous_condition: 0,
      refus: 0,
    };
    for (const score of historicalScores) {
      const probability = probabiliteDepuisScore(score, scorecardParameters);
      counts[trancheDepuisProbabilite(probability, gridParameters)] += 1;
    }
    return counts;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historicalScores, margin, lgd, approvalMultiplier]);

  function count(tranche: string): number {
    return distribution[tranche] ?? 0;
  }

  const total = historicalScores.length;
  const approvalRate = total > 0 ? (count("accord") + count("accord_sous_condition")) / total : 0;

  return (
    <Tabs defaultValue="seuils" className="gap-6">
      <TabsList>
        <TabsTrigger value="seuils">Seuils</TabsTrigger>
        <TabsTrigger value="simulation">Simulation d&rsquo;impact</TabsTrigger>
      </TabsList>

      <TabsContent value="seuils">
        <ThresholdsTab
          preset={preset}
          onPresetChange={setPreset}
          margin={margin}
          onMarginChange={setMargin}
          lgd={lgd}
          onLgdChange={setLgd}
          approvalMultiplier={approvalMultiplier}
          onApprovalMultiplierChange={setApprovalMultiplier}
          threshold={threshold}
          scorecardParameters={scorecardParameters}
          onSave={() =>
            save({
              margin,
              lgd,
              approvalMultiplier,
              productCaps: initialConfiguration.progressif.plafonds_produits,
            })
          }
          isSaving={isSaving}
          canEdit={canEdit}
        />
      </TabsContent>

      <TabsContent value="simulation">
        <SimulationTab total={total} count={count} approvalRate={approvalRate} />
      </TabsContent>
    </Tabs>
  );
}
