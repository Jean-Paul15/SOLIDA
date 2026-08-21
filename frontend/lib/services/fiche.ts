import { apiFetch } from "@/lib/services/error-service";

export async function archiveFiche(decisionId: string): Promise<void> {
  await apiFetch(`/api/v1/scoring/${decisionId}/archive`, { method: "POST" });
}
