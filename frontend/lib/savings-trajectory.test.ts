import { describe, expect, it } from "vitest";
import type { SyntheseEpargne } from "./contracts";
import { savingsTrajectory } from "./savings-trajectory";

function epargne(mouvements: SyntheseEpargne["mouvements_recents"]): SyntheseEpargne {
  return {
    solde_moyen_6m: 100000,
    tendance_12m: "stable",
    nb_mois_avec_depot_12m: 0,
    volatilite: 0,
    ratio_epargne_revenu: 0,
    anciennete_relation_mois: 24,
    mouvements_recents: mouvements,
  };
}

describe("savingsTrajectory", () => {
  const maintenant = new Date(2024, 5, 15).getTime(); // 15 juin 2024

  it("agrège les mouvements par mois calendaire", () => {
    const donnees = savingsTrajectory(
      epargne([
        { date_operation: "2024-05-10T00:00:00Z", sens: "depot", montant: 50000 },
        { date_operation: "2024-06-05T00:00:00Z", sens: "retrait", montant: 20000 },
      ]),
      2,
      maintenant
    );

    expect(donnees).toHaveLength(2);
    expect(donnees[0].depots).toBe(50000);
    expect(donnees[0].retraits).toBe(0);
    expect(donnees[1].depots).toBe(0);
    expect(donnees[1].retraits).toBe(20000);
  });

  it("ancre le dernier mois sur le solde moyen et reconstruit les mois précédents", () => {
    const donnees = savingsTrajectory(
      epargne([
        { date_operation: "2024-05-10T00:00:00Z", sens: "depot", montant: 50000 },
        { date_operation: "2024-06-05T00:00:00Z", sens: "retrait", montant: 20000 },
      ]),
      2,
      maintenant
    );

    expect(donnees[1].solde).toBe(100000);
    expect(donnees[0].solde).toBe(120000);
  });

  it("renvoie des mois vides sans mouvement", () => {
    const donnees = savingsTrajectory(epargne([]), 3, maintenant);

    expect(donnees.every((m) => m.depots === 0 && m.retraits === 0)).toBe(true);
    expect(donnees.every((m) => m.solde === 100000)).toBe(true);
  });
});
