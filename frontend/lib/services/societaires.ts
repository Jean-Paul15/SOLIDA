import type { SyntheseGroupe } from "@/lib/contracts";
import { leverSiEnErreur } from "@/lib/services/erreur-service";

export async function lireGroupe(societaireId: string): Promise<SyntheseGroupe> {
  const reponse = await fetch(`/api/v1/societaires/${societaireId}/groupe`);
  await leverSiEnErreur(reponse);
  return reponse.json();
}
