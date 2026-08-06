import { redirect } from "next/navigation";
import { fetchBackend } from "@/lib/backend";

export const SESSION_COOKIE = "solida_session";

export interface Session {
  nom: string;
  role: string;
  agence: string | null;
  doit_changer_mot_de_passe: boolean;
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

/**
 * À appeler en tête de toute page protégée (hors /changer-mot-de-passe elle-même) :
 * tant que le mot de passe par défaut n'a pas été changé, aucun autre écran n'est
 * accessible.
 */
export function exigerMotDePasseAJour(session: Session | null): void {
  if (session?.doit_changer_mot_de_passe) {
    redirect("/changer-mot-de-passe");
  }
}

/**
 * Une réponse 401 signifie une session absente, expirée ou révoquée entre le passage de
 * `proxy.ts` et cet appel (ex. reconnexion ailleurs, qui révoque l'ancienne session) : jamais
 * une absence légitime de résultat. La confondre avec une liste vide ou un 404 masquerait
 * l'échec d'authentification à l'agent (audit F5) au lieu de le renvoyer se reconnecter.
 */
export function redirigerSiNonAuthentifie(reponse: Response): void {
  if (reponse.status === 401) {
    redirect("/connexion");
  }
}
