"use client";

import { useMemo, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ProductsTab } from "@/components/solida/ProductsTab";
import { ThresholdsTab } from "@/components/solida/ThresholdsTab";
import { SimulationTab } from "@/components/solida/SimulationTab";
import { useSavePolicy } from "@/components/solida/useSavePolicy";
import type { ConfigurationGrilleApi, ProduitCreditApi } from "@/lib/contracts";
import { canEditGrille } from "@/lib/roles";
import { probabiliteDepuisScore, seuilEconomique, trancheDepuisProbabilite } from "@/lib/scorecard";

interface PolitiqueCreditProps {
  historicalScores: number[];
  initialConfiguration: ConfigurationGrilleApi;
  role: string | undefined;
  products: ProduitCreditApi[];
}

type PolicyPreset = "prudent" | "equilibre" | "expansion";

export function PolitiqueCredit({
  historicalScores,
  initialConfiguration,
  role,
  products,
}: PolitiqueCreditProps) {
  const canEdit = canEditGrille(role);
  const [productCaps, setProductCaps] = useState<Record<string, number>>(
    initialConfiguration.progressif.plafonds_produits
  );
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
  const [reviewMultiplier, setReviewMultiplier] = useState(
    initialConfiguration.grille.multiplicateur_examen
  );
  const [preset, setPreset] = useState<PolicyPreset>("equilibre");

  const scorecardParameters = { pdo, scoreReference, oddsReference };
  const gridParameters = {
    marge: margin,
    lgd,
    multiplicateurAccord: approvalMultiplier,
    multiplicateurExamen: reviewMultiplier,
  };
  const threshold = seuilEconomique(gridParameters);

  const { version, isSaving, save } = useSavePolicy(initialConfiguration, canEdit);

  const distribution = useMemo(() => {
    const counts: Record<string, number> = {
      accord: 0,
      accord_sous_condition: 0,
      comite_de_credit: 0,
      refus: 0,
    };
    for (const score of historicalScores) {
      const probability = probabiliteDepuisScore(score, scorecardParameters);
      counts[trancheDepuisProbabilite(probability, gridParameters)] += 1;
    }
    return counts;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historicalScores, margin, lgd, approvalMultiplier, reviewMultiplier]);

  function count(tranche: string): number {
    return distribution[tranche] ?? 0;
  }

  const total = historicalScores.length;
  const approvalRate = total > 0 ? (count("accord") + count("accord_sous_condition")) / total : 0;

  return (
    <Tabs defaultValue="seuils" className="gap-6">
      <TabsList>
        <TabsTrigger value="seuils">Seuils</TabsTrigger>
        <TabsTrigger value="produits">Produits</TabsTrigger>
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
          reviewMultiplier={reviewMultiplier}
          onReviewMultiplierChange={setReviewMultiplier}
          threshold={threshold}
          scorecardParameters={scorecardParameters}
          onSave={() =>
            save({
              margin,
              lgd,
              approvalMultiplier,
              reviewMultiplier,
              productCaps,
            })
          }
          isSaving={isSaving}
          canEdit={canEdit}
        />
      </TabsContent>

      <TabsContent value="produits">
        <ProductsTab
          products={products}
          productCaps={productCaps}
          onProductCapChange={(produitId, value) =>
            setProductCaps((previous) => ({ ...previous, [produitId]: value }))
          }
          canEdit={canEdit}
          version={version}
        />
      </TabsContent>

      <TabsContent value="simulation">
        <SimulationTab total={total} count={count} approvalRate={approvalRate} />
      </TabsContent>
    </Tabs>
  );
}
