import { describe, expect, it } from "vitest";
import { calculerEcheanceMensuelle, calculerTauxEndettement } from "./credit";

describe("calculerEcheanceMensuelle", () => {
  it("applique la formule d'annuité constante à taux mensuel positif", () => {
    // Vérifié indépendamment : i=0.015, n=12 -> facteur (1.015)^12 ≈ 1.195618
    // echeance = 1 200 000 * 0.015 * 1.195618 / (1.195618 - 1) ≈ 110 016
    expect(calculerEcheanceMensuelle(1200000, 12, 0.015)).toBe(110016);
  });

  it("se réduit à une répartition linéaire à taux nul", () => {
    expect(calculerEcheanceMensuelle(1200000, 12, 0)).toBe(100000);
  });

  it("renvoie zéro si la durée est nulle ou négative", () => {
    expect(calculerEcheanceMensuelle(1200000, 0, 0.015)).toBe(0);
    expect(calculerEcheanceMensuelle(1200000, -3, 0.015)).toBe(0);
  });
});

describe("calculerTauxEndettement", () => {
  it("additionne charges et échéance sur le revenu", () => {
    expect(calculerTauxEndettement(40000, 200000, 60000)).toBeCloseTo(0.5);
  });

  it("renvoie zéro si le revenu est nul ou négatif", () => {
    expect(calculerTauxEndettement(40000, 0, 60000)).toBe(0);
  });
});
