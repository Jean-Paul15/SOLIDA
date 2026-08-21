import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiFetch, throwIfError } from "./error-service";

function reponse(status: number, corps: unknown): Response {
  return new Response(JSON.stringify(corps), { status });
}

async function attendreApiError(promesse: Promise<unknown>): Promise<ApiError> {
  try {
    await promesse;
  } catch (e) {
    expect(e).toBeInstanceOf(ApiError);
    return e as ApiError;
  }
  throw new Error("La promesse aurait dû rejeter.");
}

describe("throwIfError", () => {
  it("ne lance rien sur une réponse ok", async () => {
    await expect(throwIfError(new Response(null, { status: 200 }))).resolves.toBeUndefined();
  });

  it("classe une erreur métier {code,message}", async () => {
    const erreur = await attendreApiError(
      throwIfError(
        reponse(409, {
          code: "version_grille_deja_existante",
          message: "Cette version existe déjà.",
        })
      )
    );
    expect(erreur.kind).toBe("metier");
    expect(erreur.code).toBe("version_grille_deja_existante");
    expect(erreur.message).toBe("Cette version existe déjà.");
  });

  it("classe un 401 hors route d'authentification comme session expirée", async () => {
    const erreur = await attendreApiError(throwIfError(reponse(401, { detail: "Unauthorized" })));
    expect(erreur.kind).toBe("session_expiree");
  });

  it("classe un 401 sur la route d'authentification comme le detail du backend", async () => {
    const erreur = await attendreApiError(
      throwIfError(reponse(401, { detail: "Identifiant ou mot de passe incorrect." }), {
        authRoute: true,
      })
    );
    expect(erreur.kind).toBe("serveur");
    expect(erreur.message).toBe("Identifiant ou mot de passe incorrect.");
  });

  it("classe un 403 comme accès refusé", async () => {
    const erreur = await attendreApiError(throwIfError(reponse(403, { detail: "Forbidden" })));
    expect(erreur.kind).toBe("acces_refuse");
  });

  it("classe un 429 en reprenant le detail du backend", async () => {
    const erreur = await attendreApiError(
      throwIfError(
        reponse(429, {
          detail: "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard.",
        })
      )
    );
    expect(erreur.kind).toBe("limite_atteinte");
    expect(erreur.message).toBe(
      "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard."
    );
  });

  it("classe une erreur de validation Pydantic native (detail en liste)", async () => {
    const erreur = await attendreApiError(
      throwIfError(
        reponse(422, {
          detail: [{ loc: ["body", "montant"], msg: "champ requis", type: "missing" }],
        })
      )
    );
    expect(erreur.kind).toBe("validation");
    expect(erreur.details).toHaveLength(1);
  });

  it("classe une 500 sans forme reconnue comme erreur serveur générique", async () => {
    const erreur = await attendreApiError(throwIfError(new Response("panne", { status: 500 })));
    expect(erreur.kind).toBe("serveur");
  });
});

describe("apiFetch", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("classe un échec réseau (fetch qui rejette) comme erreur réseau", async () => {
    vi.spyOn(global, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));
    const erreur = await attendreApiError(apiFetch("/api/v1/societaires/recent"));
    expect(erreur.kind).toBe("reseau");
  });

  it("renvoie la réponse telle quelle quand tout va bien", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(reponse(200, { ok: true }));
    const resultat = await apiFetch("/api/v1/societaires/recent");
    expect(resultat.ok).toBe(true);
  });
});
