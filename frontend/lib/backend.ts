import { cookies } from "next/headers";

const BACKEND_INTERNAL_URL = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

/**
 * Fetch côté serveur (Server Component) vers le backend réel : le navigateur passe par la
 * réécriture de `next.config.ts` et envoie ses cookies automatiquement, mais un fetch lancé
 * depuis le serveur Next.js n'a pas de navigateur pour le faire ; le cookie de session doit
 * être transmis explicitement, sinon le backend voit une requête non authentifiée.
 */
export async function fetchBackend(path: string, init?: RequestInit): Promise<Response> {
  const cookieHeader = (await cookies()).toString();
  return fetch(`${BACKEND_INTERNAL_URL}${path}`, {
    ...init,
    headers: { ...init?.headers, cookie: cookieHeader },
    cache: "no-store",
  });
}
