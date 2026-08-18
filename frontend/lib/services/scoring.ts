import type { EntreeScoring, ResultatScoring } from "@/lib/contracts";
import { throwIfError } from "@/lib/services/error-service";

async function post(path: string, input: EntreeScoring): Promise<ResultatScoring> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  await throwIfError(response);
  return response.json();
}

/** Calcule le score sans l'enregistrer : l'agent doit encore confirmer explicitement. */
export function previewScore(input: EntreeScoring): Promise<ResultatScoring> {
  return post("/api/v1/scoring/previsualiser", input);
}

/** Persiste la décision pour de bon, à n'appeler qu'après validation explicite de l'agent. */
export function confirmDecision(input: EntreeScoring): Promise<ResultatScoring> {
  return post("/api/v1/scoring/confirmer", input);
}
