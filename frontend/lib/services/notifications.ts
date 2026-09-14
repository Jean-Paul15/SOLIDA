import type { AgentAgenceApi, PageNotificationsApi } from "@/lib/contracts";
import { apiFetch } from "@/lib/services/error-service";

export async function fetchNotifications(limite = 20): Promise<PageNotificationsApi> {
  const response = await apiFetch(`/api/v1/notifications?limite=${limite}`);
  return response.json();
}

export async function archiveNotification(demandeId: string): Promise<void> {
  await apiFetch(`/api/v1/notifications/${demandeId}/archiver`, { method: "POST" });
}

export async function assignNotification(demandeId: string, agentId: string): Promise<void> {
  await apiFetch(`/api/v1/notifications/${demandeId}/assigner`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_id: agentId }),
  });
}

export async function fetchAgentsAgence(agenceId?: string): Promise<AgentAgenceApi[]> {
  const query = agenceId ? `?agence_id=${encodeURIComponent(agenceId)}` : "";
  const response = await apiFetch(`/api/v1/notifications/agents${query}`);
  return response.json();
}
