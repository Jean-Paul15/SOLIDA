import type { ResultatScoring } from "@/lib/contracts";

interface DecisionEnregistree {
  societaireId: string;
  resultat: ResultatScoring;
}

declare global {
  var __solidaDecisionsMock: Map<string, DecisionEnregistree> | undefined;
}

// globalThis (et non un simple module-level const) : Turbopack en mode dev peut charger ce module
// dans plus d'une instance selon le graphe (routeur HTTP vs page), ce qui viderait une Map locale
// entre l'ecriture et la lecture. globalThis est un singleton au niveau du processus Node, insensible
// a cette duplication.
const decisions = globalThis.__solidaDecisionsMock ?? new Map<string, DecisionEnregistree>();
globalThis.__solidaDecisionsMock = decisions;

export function enregistrerDecision(
  societaireId: string,
  resultatSansId: Omit<ResultatScoring, "decision_id">
): ResultatScoring {
  const decisionId = crypto.randomUUID();
  const resultat: ResultatScoring = { ...resultatSansId, decision_id: decisionId };
  decisions.set(decisionId, { societaireId, resultat });
  return resultat;
}

export function lireDecision(decisionId: string): DecisionEnregistree | undefined {
  return decisions.get(decisionId);
}
