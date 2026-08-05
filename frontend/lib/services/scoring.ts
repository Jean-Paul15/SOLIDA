import type { EntreeScoring, ResultatScoring } from "@/lib/contracts";
import { leverSiEnErreur } from "@/lib/services/erreur-service";

async function poster(chemin: string, entree: EntreeScoring): Promise<ResultatScoring> {
  const reponse = await fetch(chemin, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entree),
  });
  await leverSiEnErreur(reponse);
  return reponse.json();
}

/** Calcule le score sans l'enregistrer : l'agent doit encore confirmer explicitement. */
export function previsualiserScore(entree: EntreeScoring): Promise<ResultatScoring> {
  return poster("/api/v1/scoring/previsualiser", entree);
}

/** Persiste la décision pour de bon, à n'appeler qu'après validation explicite de l'agent. */
export function confirmerDecision(entree: EntreeScoring): Promise<ResultatScoring> {
  return poster("/api/v1/scoring/confirmer", entree);
}
