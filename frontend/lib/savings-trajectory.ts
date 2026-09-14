import type { PointSoldeMensuel, SyntheseEpargne } from "./contracts";

export interface SavingsMonth {
  horodatage: number;
  net: number;
  depots: number;
  retraits: number;
  solde: number;
}

function toSavingsMonth(point: PointSoldeMensuel): SavingsMonth {
  return {
    horodatage: new Date(point.mois).getTime(),
    net: point.total_depots - point.total_retraits,
    depots: point.total_depots,
    retraits: point.total_retraits,
    solde: point.solde_fin_mois,
  };
}

/**
 * Intersection entre la fenêtre demandée et l'historique réellement disponible
 * (`mois_affiches = min(fenêtre_demandée, ancienneté_épargne)`, §5.14) : jamais complétée par
 * des zéros, jamais tronquée pour masquer une option de fenêtre plus longue.
 */
export function selectHorizon(epargne: SyntheseEpargne, monthsHorizon: number): SavingsMonth[] {
  const serie = epargne.serie_solde_12m.slice(-monthsHorizon);
  return serie.map(toSavingsMonth);
}
