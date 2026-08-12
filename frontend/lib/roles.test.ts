import { describe, expect, it } from "vitest";
import { peutAccederPolitiqueCredit, peutModifierGrille, peutScorer } from "./roles";

describe("peutScorer", () => {
  it("autorise uniquement l'agent", () => {
    expect(peutScorer("agent")).toBe(true);
  });

  it("refuse superviseur, auditeur, administrateur et rôle absent", () => {
    // Séparation des devoirs : celui qui paramètre la grille de scoring ne doit pas
    // pouvoir aussi octroyer lui-même un crédit avec ces mêmes règles.
    expect(peutScorer("superviseur")).toBe(false);
    expect(peutScorer("auditeur")).toBe(false);
    expect(peutScorer("administrateur")).toBe(false);
    expect(peutScorer(undefined)).toBe(false);
  });
});

describe("peutModifierGrille", () => {
  it("autorise uniquement le superviseur", () => {
    expect(peutModifierGrille("superviseur")).toBe(true);
    expect(peutModifierGrille("agent")).toBe(false);
    expect(peutModifierGrille("auditeur")).toBe(false);
    expect(peutModifierGrille("administrateur")).toBe(false);
    expect(peutModifierGrille(undefined)).toBe(false);
  });
});

describe("peutAccederPolitiqueCredit", () => {
  it("autorise superviseur, auditeur et administrateur", () => {
    expect(peutAccederPolitiqueCredit("superviseur")).toBe(true);
    expect(peutAccederPolitiqueCredit("auditeur")).toBe(true);
    expect(peutAccederPolitiqueCredit("administrateur")).toBe(true);
  });

  it("refuse l'agent et l'absence de rôle", () => {
    expect(peutAccederPolitiqueCredit("agent")).toBe(false);
    expect(peutAccederPolitiqueCredit(undefined)).toBe(false);
  });
});
