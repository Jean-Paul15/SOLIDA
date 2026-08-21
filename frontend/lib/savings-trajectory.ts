import type { SyntheseEpargne } from "./contracts";

export interface SavingsMonth {
  horodatage: number;
  net: number;
  depots: number;
  retraits: number;
  solde: number;
}

function monthStart(horodatage: number): Date {
  const d = new Date(horodatage);
  return new Date(d.getFullYear(), d.getMonth(), 1);
}

/**
 * Agrège les mouvements réels par mois calendaire (net dépôts - retraits) sur les
 * `monthsHorizon` derniers mois, jamais un point par mouvement brut.
 *
 * Ancre le dernier mois sur le solde moyen (6 mois) et reconstruit les mois précédents
 * en retirant le mouvement net du mois suivant : CORE-SIM n'expose pas de solde mensuel
 * absolu (voir consulter_dossier.py), seuls les mouvements réels et cette ancre sont
 * mesurés.
 */
export function savingsTrajectory(
  epargne: SyntheseEpargne,
  monthsHorizon: number,
  maintenant: number
): SavingsMonth[] {
  const moisCourant = monthStart(maintenant);
  const mois = Array.from({ length: monthsHorizon }, (_, i) => {
    const d = new Date(
      moisCourant.getFullYear(),
      moisCourant.getMonth() - (monthsHorizon - 1 - i),
      1
    );
    const finMois = new Date(d.getFullYear(), d.getMonth() + 1, 1).getTime();
    const mouvementsDuMois = epargne.mouvements_recents.filter((m) => {
      const t = new Date(m.date_operation).getTime();
      return t >= d.getTime() && t < finMois;
    });
    const depots = mouvementsDuMois
      .filter((m) => m.sens === "depot")
      .reduce((s, m) => s + m.montant, 0);
    const retraits = mouvementsDuMois
      .filter((m) => m.sens === "retrait")
      .reduce((s, m) => s + m.montant, 0);
    return { horodatage: d.getTime(), net: depots - retraits, depots, retraits };
  });

  const soldesFinDeMois: number[] = new Array(mois.length);
  let solde = epargne.solde_moyen_6m;
  for (let i = mois.length - 1; i >= 0; i--) {
    soldesFinDeMois[i] = solde;
    solde -= mois[i].net;
  }
  return mois.map((m, i) => ({ ...m, solde: soldesFinDeMois[i] }));
}
