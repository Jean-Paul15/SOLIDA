import { useMemo, useState } from "react";
import type { DecisionRegistreVue } from "@/components/solida/RegistreDecisions";

export const TOUS = "__tous__";

export function useRegistryFilters(decisions: DecisionRegistreVue[]) {
  const [maintenant] = useState(() => Date.now());
  const [periode, setPeriode] = useState("30");
  const [agence, setAgence] = useState(TOUS);
  const [agent, setAgent] = useState(TOUS);
  const [tranche, setTranche] = useState(TOUS);

  const agences = useMemo(() => [...new Set(decisions.map((d) => d.agence))].sort(), [decisions]);
  const agents = useMemo(() => [...new Set(decisions.map((d) => d.agentName))].sort(), [decisions]);

  const filtered = useMemo(() => {
    const seuil = periode === "tout" ? null : maintenant - Number(periode) * 24 * 60 * 60 * 1000;
    return decisions.filter((d) => {
      if (seuil !== null && new Date(d.timestamp).getTime() < seuil) return false;
      if (agence !== TOUS && d.agence !== agence) return false;
      if (agent !== TOUS && d.agentName !== agent) return false;
      if (tranche !== TOUS && d.result.tranche !== tranche) return false;
      return true;
    });
  }, [decisions, periode, agence, agent, tranche, maintenant]);

  return {
    periode,
    setPeriode,
    agence,
    setAgence,
    agent,
    setAgent,
    tranche,
    setTranche,
    agences,
    agents,
    filtered,
  };
}
