import { describe, expect, it } from "vitest";
import { zoneBounds, gaugePosition, gaugeSegments, SCORE_MAX, SCORE_MIN } from "./score-gauge";

describe("gaugePosition", () => {
  it("place le score minimal à 0%", () => {
    expect(gaugePosition(SCORE_MIN)).toBe(0);
  });

  it("place le score maximal à 100%", () => {
    expect(gaugePosition(SCORE_MAX)).toBe(100);
  });

  it("borne un score hors plage", () => {
    expect(gaugePosition(SCORE_MIN - 100)).toBe(0);
    expect(gaugePosition(SCORE_MAX + 100)).toBe(100);
  });

  it("place un score médian proportionnellement", () => {
    const milieu = (SCORE_MIN + SCORE_MAX) / 2;
    expect(gaugePosition(milieu)).toBeCloseTo(50, 5);
  });
});

describe("zoneBounds et gaugeSegments", () => {
  const configuration = {
    version_grille: "v1",
    grille: {
      marge: 0.1,
      lgd: 0.5,
      multiplicateur_accord: 0.6,
    },
    progressif: {
      coefficient_progression: 1.5,
      montant_plancher: 50000,
      plafond_primo_emprunteur: 150000,
      plafonds_produits: {},
      modulation_base: 1.3,
      modulation_pente: 2.0,
      modulation_min: 0.4,
      modulation_max: 1.2,
    },
    scorecard: { pdo: 20, score_reference: 600, odds_reference: 50 },
    auteur: "test",
    date_activation: "2024-01-01T00:00:00Z",
    active: true,
  };

  it("produit 3 segments couvrant toute la jauge dans l'ordre croissant", () => {
    const segments = gaugeSegments(zoneBounds(configuration));

    expect(segments.map((s) => s.tranche)).toEqual(["refus", "accord_sous_condition", "accord"]);
    expect(segments[0].gauche).toBe(0);
    expect(segments[segments.length - 1].droite).toBe(100);
    for (let i = 1; i < segments.length; i++) {
      expect(segments[i].gauche).toBe(segments[i - 1].droite);
    }
  });
});
