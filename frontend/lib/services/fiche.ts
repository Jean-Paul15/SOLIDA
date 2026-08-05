import { leverSiEnErreur } from "@/lib/services/erreur-service";

export async function archiverFiche(decisionId: string): Promise<void> {
  const reponse = await fetch(`/api/v1/scoring/${decisionId}/archiver`, { method: "POST" });
  await leverSiEnErreur(reponse);
}
