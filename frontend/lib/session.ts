import { cookies } from "next/headers";

export const SESSION_COOKIE = "solida_session";

export interface Session {
  identifiant: string;
  nom: string;
  agence: string;
}

export async function creerSession(session: Session) {
  const store = await cookies();
  store.set(SESSION_COOKIE, Buffer.from(JSON.stringify(session)).toString("base64url"), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 8,
  });
}

export async function lireSession(): Promise<Session | null> {
  const store = await cookies();
  const valeur = store.get(SESSION_COOKIE)?.value;
  if (!valeur) return null;
  try {
    return JSON.parse(Buffer.from(valeur, "base64url").toString("utf-8"));
  } catch {
    return null;
  }
}

export async function detruireSession() {
  const store = await cookies();
  store.delete(SESSION_COOKIE);
}
