import { describe, expect, it } from "vitest";
import { safeRelativePath } from "./redirect";

describe("safeRelativePath", () => {
  it("accepte un chemin relatif interne", () => {
    expect(safeRelativePath("/dashboard")).toBe("/dashboard");
    expect(safeRelativePath("/scoring/123/fiche")).toBe("/scoring/123/fiche");
  });

  it("replie sur / en l'absence de valeur", () => {
    expect(safeRelativePath(null)).toBe("/");
    expect(safeRelativePath("")).toBe("/");
  });

  it("rejette une URL absolue (open redirect)", () => {
    expect(safeRelativePath("https://evil.example.com")).toBe("/");
    expect(safeRelativePath("http://evil.example.com/fake-session-expired")).toBe("/");
  });

  it("rejette un chemin protocol-relative", () => {
    expect(safeRelativePath("//evil.example.com")).toBe("/");
  });

  it("rejette un schéma non-http", () => {
    expect(safeRelativePath("javascript:alert(1)")).toBe("/");
  });
});
