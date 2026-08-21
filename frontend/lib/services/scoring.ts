import type { ScoringInput, ScoringResult } from "@/lib/contracts";
import { apiFetch } from "@/lib/services/error-service";

async function post(path: string, input: ScoringInput): Promise<ScoringResult> {
  const response = await apiFetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return response.json();
}

/** Calcule le score sans l'enregistrer : l'agent doit encore confirmer explicitement. */
export function previewScore(input: ScoringInput): Promise<ScoringResult> {
  return post("/api/v1/scoring/preview", input);
}

/** Persiste la décision pour de bon, à n'appeler qu'après validation explicite de l'agent. */
export function confirmDecision(input: ScoringInput): Promise<ScoringResult> {
  return post("/api/v1/scoring/confirm", input);
}
