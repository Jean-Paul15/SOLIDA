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
  scoresHistoriques: number[];
  configurationInitiale: ConfigurationGrilleApi;
  role: string | undefined;
  produits: ProduitCreditApi[];
}

type Preregl = "prudent" | "equilibre" | "expansion";

export function PolitiqueCredit({
  scoresHistoriques,
  configurationInitiale,
  role,
  produits,
}: PolitiqueCreditProps) {
  const autoriseAModifier = canEditGrille(role);
  const [plafondsProduits, setPlafondsProduits] = useState<Record<string, number>>(
    configurationInitiale.progressif.plafonds_produits
  );
  // PDO, score de référence et rapport de référence ne sont plus édités depuis cet écran
  // (administration du modèle hors périmètre SOLIDA) : ils sont retransmis inchangés à
  // l'enregistrement.
  const {
    pdo,
    score_reference: scoreReference,
    odds_reference: oddsReference,
  } = configurationInitiale.scorecard;
  const [marge, setMarge] = useState(configurationInitiale.grille.marge);
  const [lgd, setLgd] = useState(configurationInitiale.grille.lgd);
  const [multiplicateurAccord, setMultiplicateurAccord] = useState(
    configurationInitiale.grille.multiplicateur_accord
  );
  const [multiplicateurExamen, setMultiplicateurExamen] = useState(
    configurationInitiale.grille.multiplicateur_examen
  );
  const [preregl, setPreregl] = useState<Preregl>("equilibre");

  const parametresScorecard = { pdo, scoreReference, oddsReference };
  const parametresGrille = { marge, lgd, multiplicateurAccord, multiplicateurExamen };
  const seuil = seuilEconomique(parametresGrille);

  const { version, enregistrementEnCours, enregistrer } = useSavePolicy(
    configurationInitiale,
    autoriseAModifier
  );

  const repartition = useMemo(() => {
    const compte: Record<string, number> = {
      accord: 0,
      accord_sous_condition: 0,
      comite_de_credit: 0,
      refus: 0,
    };
    for (const score of scoresHistoriques) {
      const p = probabiliteDepuisScore(score, parametresScorecard);
      compte[trancheDepuisProbabilite(p, parametresGrille)] += 1;
    }
    return compte;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scoresHistoriques, marge, lgd, multiplicateurAccord, multiplicateurExamen]);

  function compte(tranche: string): number {
    return repartition[tranche] ?? 0;
  }

  const total = scoresHistoriques.length;
  const tauxApprobation =
    total > 0 ? (compte("accord") + compte("accord_sous_condition")) / total : 0;

  return (
    <Tabs defaultValue="seuils" className="gap-6">
      <TabsList>
        <TabsTrigger value="seuils">Seuils</TabsTrigger>
        <TabsTrigger value="produits">Produits</TabsTrigger>
        <TabsTrigger value="simulation">Simulation d&rsquo;impact</TabsTrigger>
      </TabsList>

      <TabsContent value="seuils">
        <ThresholdsTab
          preregl={preregl}
          onChangePreregl={setPreregl}
          marge={marge}
          onChangeMarge={setMarge}
          lgd={lgd}
          onChangeLgd={setLgd}
          multiplicateurAccord={multiplicateurAccord}
          onChangeMultiplicateurAccord={setMultiplicateurAccord}
          multiplicateurExamen={multiplicateurExamen}
          onChangeMultiplicateurExamen={setMultiplicateurExamen}
          seuil={seuil}
          parametresScorecard={parametresScorecard}
          enregistrer={() =>
            enregistrer({
              marge,
              lgd,
              multiplicateurAccord,
              multiplicateurExamen,
              plafondsProduits,
            })
          }
          enregistrementEnCours={enregistrementEnCours}
          autoriseAModifier={autoriseAModifier}
        />
      </TabsContent>

      <TabsContent value="produits">
        <ProductsTab
          produits={produits}
          plafondsProduits={plafondsProduits}
          onChangePlafond={(produitId, valeur) =>
            setPlafondsProduits((precedent) => ({ ...precedent, [produitId]: valeur }))
          }
          autoriseAModifier={autoriseAModifier}
          version={version}
        />
      </TabsContent>

      <TabsContent value="simulation">
        <SimulationTab total={total} compte={compte} tauxApprobation={tauxApprobation} />
      </TabsContent>
    </Tabs>
  );
}
