import type { SyntheseGroupe } from "@/lib/contracts";
import { apiFetch } from "@/lib/services/error-service";

export async function fetchGroup(societaireId: string): Promise<SyntheseGroupe> {
  const response = await apiFetch(`/api/v1/societaires/${societaireId}/groupe`);
  return response.json();
}
