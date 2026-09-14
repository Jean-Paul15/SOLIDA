import { toast } from "sonner";

export type ApiErrorKind =
  | "session_expired"
  | "domain"
  | "validation"
  | "rate_limited"
  | "server"
  | "network";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly code: string;
  readonly status: number;
  readonly details?: unknown;

  constructor(
    kind: ApiErrorKind,
    code: string,
    status: number,
    message: string,
    details?: unknown,
  ) {
    super(message);
    this.kind = kind;
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

const DEFAULT_MESSAGE: Record<Exclude<ApiErrorKind, "domain">, string> = {
  session_expired: "Votre session a expiré, recommencez depuis l'accueil.",
  validation: "Une information saisie n'est pas valide. Vérifiez et réessayez.",
  rate_limited: "Trop de tentatives. Réessayez dans quelques minutes.",
  server: "Une erreur technique est survenue. Réessayez dans un instant.",
  network:
    "Connexion impossible pour le moment. Votre demande est conservée sur ce téléphone.",
};

/**
 * Même forme que le pendant agent (frontend/lib/services/error-service.ts) : trois
 * types de payload backend — {code,message} aplati (DomainError), {detail:
 * {code,message}} imbriqué (HTTPException levée directement dans un routeur, ex.
 * "session_expiree" dans portail.py::_jeton_bearer), ou {detail} FastAPI natif pour
 * le reste — mais pas de notion d'accès refusé (aucun rôle côté sociétaire) ni de
 * redirection vers un écran de connexion (il n'y en a pas ici, cf. section 2 du
 * parcours).
 */
export async function throwIfError(response: Response): Promise<void> {
  if (response.ok) return;
  const body = await response.json().catch(() => null);

  if (typeof body?.code === "string" && typeof body?.message === "string") {
    throw new ApiError(
      "domain",
      body.code,
      response.status,
      body.message,
      body.details,
    );
  }

  if (
    body?.detail &&
    typeof body.detail === "object" &&
    !Array.isArray(body.detail) &&
    typeof body.detail.code === "string" &&
    typeof body.detail.message === "string"
  ) {
    throw new ApiError(
      "domain",
      body.detail.code,
      response.status,
      body.detail.message,
      body.detail.details,
    );
  }

  if (response.status === 401) {
    throw new ApiError(
      "session_expired",
      "session_expired",
      401,
      DEFAULT_MESSAGE.session_expired,
    );
  }

  if (response.status === 429) {
    const message =
      typeof body?.detail === "string"
        ? body.detail
        : DEFAULT_MESSAGE.rate_limited;
    throw new ApiError("rate_limited", "rate_limited", 429, message);
  }

  if (Array.isArray(body?.detail)) {
    throw new ApiError(
      "validation",
      "validation_failed",
      response.status,
      DEFAULT_MESSAGE.validation,
      body.detail,
    );
  }

  if (typeof body?.detail === "string") {
    throw new ApiError("server", "server_error", response.status, body.detail);
  }

  throw new ApiError(
    "server",
    "server_error",
    response.status,
    DEFAULT_MESSAGE.server,
  );
}

export async function apiFetch(
  input: string,
  init?: RequestInit,
): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(input, init);
  } catch {
    throw new ApiError("network", "network_error", 0, DEFAULT_MESSAGE.network);
  }
  await throwIfError(response);
  return response;
}

export function afficherErreur(error: unknown, repli: string): void {
  toast.error(error instanceof ApiError ? error.message : repli);
}
