import { redirect } from "next/navigation";
import { fetchBackend } from "@/lib/backend";

export const SESSION_COOKIE = "solida_session";

export interface Session {
  name: string;
  role: string;
  agence: string | null;
  must_change_password: boolean;
}

/**
 * Relit la session depuis le backend (`GET /api/v1/auth/me`) plutôt que de décoder le
 * cookie côté frontend : le cookie est un jeton opaque géré par FastAPI-Users, le frontend
 * n'a aucun moyen de le lire ni de lui faire confiance directement.
 */
export async function readSession(): Promise<Session | null> {
  const response = await fetchBackend("/api/v1/auth/me");
  if (!response.ok) return null;
  return response.json();
}

/**
 * À appeler en tête de toute page protégée (hors /changer-mot-de-passe elle-même) :
 * tant que le mot de passe par défaut n'a pas été changé, aucun autre écran n'est
 * accessible.
 */
export function enforcePasswordUpToDate(session: Session | null): void {
  if (session?.must_change_password) {
    redirect("/changer-mot-de-passe");
  }
}

/**
 * Une réponse 401 signifie une session absente, expirée ou révoquée entre le passage de
 * `proxy.ts` et cet appel (ex. reconnexion ailleurs, qui révoque l'ancienne session) : jamais
 * une absence légitime de résultat. La confondre avec une liste vide ou un 404 masquerait
 * l'échec d'authentification à l'agent (audit F5) au lieu de le renvoyer se reconnecter.
 */
export function redirectIfUnauthenticated(response: Response): void {
  if (response.status === 401) {
    redirect("/connexion");
  }
}

/**
 * Un 403 signifie que la ressource existe mais que l'agent n'a pas le droit de la voir
 * (ex. sociétaire d'une autre agence, voir `AccesRefuse` côté backend) : ne jamais le
 * confondre avec `notFound()`, qui affiche « page introuvable » et masquerait à l'agent
 * qu'il vient de heurter une frontière d'accès plutôt qu'un identifiant invalide.
 */
export function redirectIfAccessDenied(response: Response): void {
  if (response.status === 403) {
    redirect("/acces-refuse");
  }
}
