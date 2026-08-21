/**
 * Amortissement à annuité constante (méthode actuarielle) : c'est la méthode que la
 * réglementation BCEAO impose pour exprimer le TEG/TAEG des crédits dans l'UEMOA, et
 * celle qu'appliquent en pratique les coopératives d'épargne et de crédit togolaises
 * (intérêt dégressif sur le capital restant dû, pas un taux forfaitaire sur le montant
 * initial).
 *
 * echeance = montant × [i × (1+i)^n] / [(1+i)^n − 1], où i est le taux mensuel.
 */
export function calculateMonthlyInstallment(
  montantDemande: number,
  dureeMois: number,
  tauxMensuel: number
): number {
  if (dureeMois <= 0) return 0;
  if (tauxMensuel === 0) return Math.round(montantDemande / dureeMois);

  const facteur = Math.pow(1 + tauxMensuel, dureeMois);
  return Math.round((montantDemande * tauxMensuel * facteur) / (facteur - 1));
}

// Le TAEG plafond BCEAO pour les SFD est de 24 % l'an (UEMOA, depuis le 1er juin 2026).
// Cette valeur est un taux de démonstration, largement sous le plafond, en l'absence
// d'une table de taux par produit de crédit : à remplacer dès qu'elle existe.
export const TAUX_MENSUEL_DEMONSTRATION = 0.18 / 12;

export function calculateDebtRatio(
  chargesMensuelles: number,
  revenuMensuel: number,
  echeanceMensuelle: number
): number {
  if (revenuMensuel <= 0) return 0;
  return (chargesMensuelles + echeanceMensuelle) / revenuMensuel;
}
