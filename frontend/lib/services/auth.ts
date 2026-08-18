import { throwIfError } from "@/lib/services/error-service";

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  const response = await fetch("/api/v1/auth/changer-mot-de-passe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mot_de_passe_actuel: currentPassword,
      nouveau_mot_de_passe: newPassword,
    }),
  });
  await throwIfError(response);
}
