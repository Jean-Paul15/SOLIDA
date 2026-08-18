import { throwIfError } from "@/lib/services/error-service";

export async function archiveFiche(decisionId: string): Promise<void> {
  const response = await fetch(`/api/v1/scoring/${decisionId}/archiver`, { method: "POST" });
  await throwIfError(response);
}
