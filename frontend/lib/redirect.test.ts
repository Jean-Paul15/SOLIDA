import { describe, expect, it } from "vitest";
import { cheminRelatifSur } from "./redirect";

describe("cheminRelatifSur", () => {
  it("accepte un chemin relatif interne", () => {
    expect(cheminRelatifSur("/dashboard")).toBe("/dashboard");
    expect(cheminRelatifSur("/scoring/123/fiche")).toBe("/scoring/123/fiche");
  });

  it("replie sur / en l'absence de valeur", () => {
    expect(cheminRelatifSur(null)).toBe("/");
    expect(cheminRelatifSur("")).toBe("/");
  });

  it("rejette une URL absolue (open redirect)", () => {
    expect(cheminRelatifSur("https://evil.example.com")).toBe("/");
    expect(cheminRelatifSur("http://evil.example.com/fake-session-expired")).toBe("/");
  });

  it("rejette un chemin protocol-relative", () => {
    expect(cheminRelatifSur("//evil.example.com")).toBe("/");
  });

  it("rejette un schéma non-http", () => {
    expect(cheminRelatifSur("javascript:alert(1)")).toBe("/");
  });
});
