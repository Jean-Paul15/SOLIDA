import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiFetch, throwIfError } from "./error-service";

function response(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status });
}

async function waitForApiError(promise: Promise<unknown>): Promise<ApiError> {
  try {
    await promise;
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
    const error = await waitForApiError(
      throwIfError(
        response(409, {
          code: "version_grille_deja_existante",
          message: "Cette version existe déjà.",
        })
      )
    );
    expect(error.kind).toBe("domain");
    expect(error.code).toBe("version_grille_deja_existante");
    expect(error.message).toBe("Cette version existe déjà.");
  });

  it("classe un 401 hors route d'authentification comme session expirée", async () => {
    const error = await waitForApiError(throwIfError(response(401, { detail: "Unauthorized" })));
    expect(error.kind).toBe("session_expired");
  });

  it("classe un 401 sur la route d'authentification comme le detail du backend", async () => {
    const error = await waitForApiError(
      throwIfError(response(401, { detail: "Identifiant ou mot de passe incorrect." }), {
        authRoute: true,
      })
    );
    expect(error.kind).toBe("server");
    expect(error.message).toBe("Identifiant ou mot de passe incorrect.");
  });

  it("classe un 403 comme accès refusé", async () => {
    const error = await waitForApiError(throwIfError(response(403, { detail: "Forbidden" })));
    expect(error.kind).toBe("access_denied");
  });

  it("classe un 429 en reprenant le detail du backend", async () => {
    const error = await waitForApiError(
      throwIfError(
        response(429, {
          detail: "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard.",
        })
      )
    );
    expect(error.kind).toBe("rate_limited");
    expect(error.message).toBe(
      "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard."
    );
  });

  it("classe une erreur de validation Pydantic native (detail en liste)", async () => {
    const error = await waitForApiError(
      throwIfError(
        response(422, {
          detail: [{ loc: ["body", "montant"], msg: "champ requis", type: "missing" }],
        })
      )
    );
    expect(error.kind).toBe("validation");
    expect(error.details).toHaveLength(1);
  });

  it("classe une 500 sans forme reconnue comme erreur serveur générique", async () => {
    const error = await waitForApiError(throwIfError(new Response("panne", { status: 500 })));
    expect(error.kind).toBe("server");
  });
});

describe("apiFetch", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("classe un échec réseau (fetch qui rejette) comme erreur réseau", async () => {
    vi.spyOn(global, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));
    const error = await waitForApiError(apiFetch("/api/v1/societaires/recent"));
    expect(error.kind).toBe("network");
  });

  it("renvoie la réponse telle quelle quand tout va bien", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(response(200, { ok: true }));
    const result = await apiFetch("/api/v1/societaires/recent");
    expect(result.ok).toBe(true);
  });
});
