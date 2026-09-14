/**
 * Reflète les rôles acceptés côté serveur (`require_role(...)` dans les routeurs FastAPI) :
 * n'affiche jamais une action que le backend refuserait, ça évite de laisser croire à l'agent
 * qu'elle a réussi puis de le confronter à un 403. Le serveur reste la seule
 * autorité réelle ; ceci ne pilote que l'affichage.
 */
export const ROLES_SCORING = ["agent"];
export const ROLES_MODIFICATION_GRILLE = ["superviseur"];
export const ROLES_POLITIQUE_CREDIT = ["superviseur", "auditeur", "administrateur"];
export const ROLES_NOTIFICATIONS = ["agent", "superviseur"];

export function canScore(role: string | undefined): boolean {
  return role !== undefined && ROLES_SCORING.includes(role);
}

export function canEditGrille(role: string | undefined): boolean {
  return role !== undefined && ROLES_MODIFICATION_GRILLE.includes(role);
}

/**
 * Contrôle l'accès à l'écran « Politique de crédit » (paramétrage de la grille), pas à l'API :
 * l'agent garde l'accès en lecture à `GET /api/v1/parametrage/grille` pour l'explicabilité de son
 * score (voir `ScoringResultView.tsx`), mais l'écran de paramétrage lui-même ne lui est pas
 * destiné.
 */
export function canAccessCreditPolicy(role: string | undefined): boolean {
  return role !== undefined && ROLES_POLITIQUE_CREDIT.includes(role);
}

/**
 * Le centre de notifications a deux visages selon le rôle (`CentreNotificationsAgent`/
 * `CentreNotificationsSuperviseur`) : l'agent traite ses demandes assignées, le superviseur
 * répartit les demandes non assignées de son agence entre ses agents.
 */
export function canAccessNotifications(role: string | undefined): boolean {
  return role !== undefined && ROLES_NOTIFICATIONS.includes(role);
}
