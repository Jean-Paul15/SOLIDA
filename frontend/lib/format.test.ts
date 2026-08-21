import { describe, expect, it } from "vitest";
import { formatAmount } from "./format";

const espace = " ";

describe("formatAmount", () => {
  it("sépare les milliers et ajoute la devise", () => {
    expect(formatAmount(1250000)).toBe(`1${espace}250${espace}000 FCFA`);
  });

  it("arrondit les décimales", () => {
    expect(formatAmount(1250000.6)).toBe(`1${espace}250${espace}001 FCFA`);
  });

  it("gère zéro", () => {
    expect(formatAmount(0)).toBe("0 FCFA");
  });
});
