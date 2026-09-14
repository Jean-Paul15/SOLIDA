import { describe, expect, it } from "vitest";
import { LISTE_OBJETS_CREDIT, OBJETS_CREDIT } from "./objets-credit";

describe("objets-credit", () => {
  it("associe chaque objet à un libellé non vide", () => {
    for (const cle of LISTE_OBJETS_CREDIT) {
      expect(OBJETS_CREDIT[cle].libelle.length).toBeGreaterThan(0);
    }
  });
});
