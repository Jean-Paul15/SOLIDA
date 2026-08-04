import type { EntreeScoring, ResultatScoring } from "@/lib/contracts";
import { leverSiEnErreur } from "@/lib/services/erreur-service";

export async function calculerScore(entree: EntreeScoring): Promise<ResultatScoring> {
  const reponse = await fetch("/api/v1/scoring", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entree),
  });
  await leverSiEnErreur(reponse);
  return reponse.json();
}
