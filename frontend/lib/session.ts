import { fetchBackend } from "@/lib/backend";

export const SESSION_COOKIE = "solida_session";

export interface Session {
  nom: string;
  agence: string | null;
}

/**
 * Relit la session depuis le backend (`GET /api/v1/auth/moi`) plutôt que de décoder le
 * cookie côté frontend : le cookie est un jeton opaque géré par FastAPI-Users, le frontend
 * n'a aucun moyen de le lire ni de lui faire confiance directement.
 */
export async function lireSession(): Promise<Session | null> {
  const reponse = await fetchBackend("/api/v1/auth/moi");
  if (!reponse.ok) return null;
  return reponse.json();
}
