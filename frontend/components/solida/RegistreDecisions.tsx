"use client";

import type { ScoringResult } from "@/lib/contracts";
import { RegistryFilters } from "./RegistryFilters";
import { DecisionsTable } from "./DecisionsTable";
import { useRegistryFilters } from "./useRegistryFilters";

export interface DecisionRegistreVue {
  decisionId: string;
  societaireId: string;
  societaireNom: string;
  agence: string;
  result: ScoringResult;
  timestamp: string;
  agentName: string;
  /** Toujours `undefined` : la finalisation d'une décision (montant réellement accordé)
   * n'est pas encore modélisée côté backend (`decision_finale`, voir
   * docs/backend/02-persistance-et-migrations.md). */
  grantedAmount?: number;
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
    filtered,
  } = useRegistryFilters(decisions);

  return (
    <div className="flex flex-col gap-4">
      <RegistryFilters
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
      <DecisionsTable filtered={filtered} />
    </div>
  );
}
