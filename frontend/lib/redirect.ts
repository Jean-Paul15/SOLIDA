/**
 * Chemin interne accepté après connexion (`/connexion?redirect=...`) : n'accepte qu'un chemin
 * relatif à cette application, jamais une URL absolue ni un chemin protocol-relative (`//host`),
 * pour empêcher toute redirection vers un domaine arbitraire choisi par l'appelant.
 */
export function safeRelativePath(valeur: string | null): string {
  if (valeur !== null && /^\/(?!\/)/.test(valeur)) {
    return valeur;
  }
  return "/";
}
