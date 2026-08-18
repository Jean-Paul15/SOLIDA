import type { SyntheseGroupe } from "@/lib/contracts";
import { throwIfError } from "@/lib/services/error-service";

export async function fetchGroup(societaireId: string): Promise<SyntheseGroupe> {
  const response = await fetch(`/api/v1/societaires/${societaireId}/groupe`);
  await throwIfError(response);
  return response.json();
}
