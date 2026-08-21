import { apiFetch } from "@/lib/services/error-service";

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await apiFetch("/api/v1/auth/change-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mot_de_passe_actuel: currentPassword,
      nouveau_mot_de_passe: newPassword,
    }),
  });
}
