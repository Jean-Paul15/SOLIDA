import { describe, expect, it } from "vitest";
import { canAccessCreditPolicy, canEditGrille, canScore } from "./roles";

describe("canScore", () => {
  it("autorise uniquement l'agent", () => {
    expect(canScore("agent")).toBe(true);
  });

  it("refuse superviseur, auditeur, administrateur et rôle absent", () => {
    // Séparation des devoirs : celui qui paramètre la grille de scoring ne doit pas
    // pouvoir aussi octroyer lui-même un crédit avec ces mêmes règles.
    expect(canScore("superviseur")).toBe(false);
    expect(canScore("auditeur")).toBe(false);
    expect(canScore("administrateur")).toBe(false);
    expect(canScore(undefined)).toBe(false);
  });
});

describe("canEditGrille", () => {
  it("autorise uniquement le superviseur", () => {
    expect(canEditGrille("superviseur")).toBe(true);
    expect(canEditGrille("agent")).toBe(false);
    expect(canEditGrille("auditeur")).toBe(false);
    expect(canEditGrille("administrateur")).toBe(false);
    expect(canEditGrille(undefined)).toBe(false);
  });
});

describe("canAccessCreditPolicy", () => {
  it("autorise superviseur, auditeur et administrateur", () => {
    expect(canAccessCreditPolicy("superviseur")).toBe(true);
    expect(canAccessCreditPolicy("auditeur")).toBe(true);
    expect(canAccessCreditPolicy("administrateur")).toBe(true);
  });

  it("refuse l'agent et l'absence de rôle", () => {
    expect(canAccessCreditPolicy("agent")).toBe(false);
    expect(canAccessCreditPolicy(undefined)).toBe(false);
  });
});
