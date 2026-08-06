/**
 * Reflète les rôles acceptés côté serveur (`exige_role(...)` dans les routeurs FastAPI) :
 * n'affiche jamais une action que le backend refuserait, ça évite de laisser croire à l'agent
 * qu'elle a réussi puis de le confronter à un 403 (audit F6). Le serveur reste la seule
 * autorité réelle ; ceci ne pilote que l'affichage.
 */
export const ROLES_SCORING = ["agent", "superviseur"];
export const ROLES_MODIFICATION_GRILLE = ["superviseur"];

export function peutScorer(role: string | undefined): boolean {
  return role !== undefined && ROLES_SCORING.includes(role);
}

export function peutModifierGrille(role: string | undefined): boolean {
  return role !== undefined && ROLES_MODIFICATION_GRILLE.includes(role);
}
