import { describe, expect, it } from "vitest";
import { LISTE_OBJETS_CREDIT, OBJETS_CREDIT } from "./objets-credit";

describe("objets-credit", () => {
  it("associe chaque objet à un libellé non vide et une divisibilité connue", () => {
    for (const cle of LISTE_OBJETS_CREDIT) {
      const definition = OBJETS_CREDIT[cle];
      expect(definition.libelle.length).toBeGreaterThan(0);
      expect(["divisible", "indivisible", "mixte"]).toContain(definition.divisibilite);
    }
  });

  it("classe l'équipement comme indivisible (jamais de montant réduit dessus)", () => {
    expect(OBJETS_CREDIT.equipement.divisibilite).toBe("indivisible");
  });

  it("classe le fonds de roulement et le stock comme divisibles", () => {
    expect(OBJETS_CREDIT.fonds_roulement.divisibilite).toBe("divisible");
    expect(OBJETS_CREDIT.stock.divisibilite).toBe("divisible");
  });
});
