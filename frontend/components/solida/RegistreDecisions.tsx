"use client";

import type { ScoringResult } from "@/lib/contracts";
import { FiltresRegistre } from "./FiltresRegistre";
import { TableauDecisions } from "./TableauDecisions";
import { useFiltresRegistre } from "./useFiltresRegistre";

export interface DecisionRegistreVue {
  decisionId: string;
  societaireId: string;
  societaireNom: string;
  agence: string;
  resultat: ScoringResult;
  horodatage: string;
  agentNom: string;
  /** Toujours `undefined` : la finalisation d'une décision (montant réellement accordé)
   * n'est pas encore modélisée côté backend (`decision_finale`, voir
   * docs/backend/02-persistance-et-migrations.md). */
  montantAccorde?: number;
}

interface RegistreDecisionsProps {
  decisions: DecisionRegistreVue[];
}

export function RegistreDecisions({ decisions }: RegistreDecisionsProps) {
  const {
    periode,
    setPeriode,
    agence,
    setAgence,
    agences,
    agent,
    setAgent,
    agents,
    tranche,
    setTranche,
    filtrees,
  } = useFiltresRegistre(decisions);

  return (
    <div className="flex flex-col gap-4">
      <FiltresRegistre
        periode={periode}
        setPeriode={setPeriode}
        agence={agence}
        setAgence={setAgence}
        agences={agences}
        agent={agent}
        setAgent={setAgent}
        agents={agents}
        tranche={tranche}
        setTranche={setTranche}
      />
      <TableauDecisions filtrees={filtrees} />
    </div>
  );
}
