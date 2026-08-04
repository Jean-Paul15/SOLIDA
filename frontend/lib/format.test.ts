import { describe, expect, it } from "vitest";
import { formaterMontant } from "./format";

const espace = " ";

describe("formaterMontant", () => {
  it("sépare les milliers et ajoute la devise", () => {
    expect(formaterMontant(1250000)).toBe(`1${espace}250${espace}000 FCFA`);
  });

  it("arrondit les décimales", () => {
    expect(formaterMontant(1250000.6)).toBe(`1${espace}250${espace}001 FCFA`);
  });

  it("gère zéro", () => {
    expect(formaterMontant(0)).toBe("0 FCFA");
  });
});
