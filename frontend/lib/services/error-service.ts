import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { toast } from "sonner";

export type ApiErrorKind =
  | "session_expired"
  | "access_denied"
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
    details?: unknown
  ) {
    super(message);
    this.kind = kind;
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

const DEFAULT_MESSAGE: Record<Exclude<ApiErrorKind, "domain">, string> = {
  session_expired: "Votre session a expiré. Reconnectez-vous.",
  access_denied: "Vous n'avez pas les droits nécessaires pour cette action.",
  validation: "La requête envoyée est invalide. Réessayez ou signalez le problème si ça persiste.",
  rate_limited: "Trop de tentatives. Réessayez plus tard.",
  server: "Une erreur technique est survenue côté serveur. Réessayez dans un instant.",
  network: "Connexion au serveur impossible. Vérifiez votre réseau et réessayez.",
};

interface ApiErrorOptions {
  /** Route d'authentification (login) : un 401 y signifie "identifiants invalides", pas "session expirée". */
  authRoute?: boolean;
}

/**
 * Classe la réponse d'erreur du backend, qui prend TROIS formes distinctes :
 * `{code, message}` aplati pour les `DomainError` (handler global,
 * `application_fastapi.py`), `{detail: {code, message}}` imbriqué pour les
 * `HTTPException(status, detail={...})` levées directement dans les routeurs (ex.
 * "introuvable", "session_expiree", "agence_requise"), et `{detail}` brut pour tout
 * le reste (422 de validation Pydantic natif, 429, 5xx non intercepté). Les deux
 * premières formes portent un message métier précis à afficher tel quel — jamais le
 * confondre avec le repli générique, qui masquerait une explication utile à l'agent.
 */
export async function throwIfError(
  response: Response,
  options: ApiErrorOptions = {}
): Promise<void> {
  if (response.ok) return;
  const body = await response.json().catch(() => null);

  if (typeof body?.code === "string" && typeof body?.message === "string") {
    throw new ApiError("domain", body.code, response.status, body.message, body.details);
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
      body.detail.details
    );
  }

  if (response.status === 401 && !options.authRoute) {
    throw new ApiError("session_expired", "session_expired", 401, DEFAULT_MESSAGE.session_expired);
  }

  if (response.status === 403) {
    throw new ApiError("access_denied", "access_denied", 403, DEFAULT_MESSAGE.access_denied);
  }

  if (response.status === 429) {
    const message = typeof body?.detail === "string" ? body.detail : DEFAULT_MESSAGE.rate_limited;
    throw new ApiError("rate_limited", "rate_limited", 429, message);
  }

  if (Array.isArray(body?.detail)) {
    throw new ApiError(
      "validation",
      "validation_failed",
      response.status,
      DEFAULT_MESSAGE.validation,
      body.detail
    );
  }

  if (typeof body?.detail === "string") {
    throw new ApiError("server", "server_error", response.status, body.detail);
  }

  throw new ApiError("server", "server_error", response.status, DEFAULT_MESSAGE.server);
}

/**
 * Enveloppe `fetch` : convertit un échec réseau (aucune réponse reçue, jamais couvert
 * par `throwIfError` qui n'agit que sur une `Response`) en `ApiError` de même forme
 * que les erreurs HTTP, pour que tous les sites d'appel n'aient qu'un seul type
 * d'erreur à traiter.
 */
export async function apiFetch(
  input: string,
  init?: RequestInit,
  options?: ApiErrorOptions
): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(input, init);
  } catch {
    throw new ApiError("network", "network_error", 0, DEFAULT_MESSAGE.network);
  }
  await throwIfError(response, options);
  return response;
}

/**
 * Réagit à une erreur d'appel API de façon uniforme : session expirée => annonce
 * explicite puis redirection vers la connexion (avec retour au bon endroit ensuite,
 * `LoginForm` lit déjà `?redirect=`) ; sinon toast avec le message précis renvoyé par
 * le backend, ou le repli fourni si l'erreur n'est pas une `ApiError`.
 */
export function useApiErrorToast() {
  const router = useRouter();

  // `router` est stable entre les rendus (App Router) : la fonction retournée l'est
  // donc aussi, ce qui permet de l'utiliser sans avertissement dans un tableau de
  // dépendances d'effet (ex. SocietaireSearch, chargement en arrière-plan).
  return useCallback(
    (error: unknown, fallback: string): void => {
      if (error instanceof ApiError && error.kind === "session_expired") {
        toast.error("Votre session a expiré. Vous allez être redirigé vers la connexion.");
        const path = encodeURIComponent(window.location.pathname);
        router.push(`/connexion?redirect=${path}`);
        return;
      }
      toast.error(error instanceof ApiError ? error.message : fallback);
    },
    [router]
  );
}
