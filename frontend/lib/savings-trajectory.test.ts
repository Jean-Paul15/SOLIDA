import { describe, expect, it } from "vitest";
import type { PointSoldeMensuel, SyntheseEpargne } from "./contracts";
import { selectHorizon } from "./savings-trajectory";

function epargne(serie: PointSoldeMensuel[]): SyntheseEpargne {
  return {
    solde_moyen_6m: 100000,
    tendance_12m: "stable",
    nb_mois_avec_depot_12m: 0,
    volatilite: 0,
    ratio_epargne_revenu: 0,
    anciennete_relation_mois: 24,
    serie_solde_12m: serie,
  };
}

function point(mois: string, solde: number, depots = 0, retraits = 0): PointSoldeMensuel {
  return { mois, solde_fin_mois: solde, total_depots: depots, total_retraits: retraits };
}

describe("selectHorizon", () => {
  it("renvoie exactement les points reçus, sans reconstruction ni interpolation", () => {
    const donnees = selectHorizon(
      epargne([point("2024-04-01", 80000, 50000, 0), point("2024-05-01", 100000, 0, 20000)]),
      12
    );

    expect(donnees).toHaveLength(2);
    expect(donnees[0].solde).toBe(80000);
    expect(donnees[0].depots).toBe(50000);
    expect(donnees[1].solde).toBe(100000);
    expect(donnees[1].retraits).toBe(20000);
  });

  it("tronque à la fenêtre demandée sans jamais compléter par des zéros", () => {
    const serie = Array.from({ length: 12 }, (_, i) =>
      point(`2024-${String(i + 1).padStart(2, "0")}-01`, 10000 * (i + 1))
    );

    const troisMois = selectHorizon(epargne(serie), 3);
    expect(troisMois).toHaveLength(3);
    expect(troisMois.map((m) => m.solde)).toEqual([100000, 110000, 120000]);
  });

  it("un historique plus court que la fenêtre demandée n'est jamais complété", () => {
    const donnees = selectHorizon(epargne([point("2024-06-01", 50000, 10000, 0)]), 12);

    expect(donnees).toHaveLength(1);
    expect(donnees[0].solde).toBe(50000);
  });

  it("un historique vide ne produit aucun point (jamais un solde à zéro inventé)", () => {
    const donnees = selectHorizon(epargne([]), 6);
    expect(donnees).toHaveLength(0);
  });
});
