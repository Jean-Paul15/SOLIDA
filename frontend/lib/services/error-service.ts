import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { toast } from "sonner";

export type ApiErrorKind =
  | "session_expiree"
  | "acces_refuse"
  | "metier"
  | "validation"
  | "limite_atteinte"
  | "serveur"
  | "reseau";

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

const MESSAGE_PAR_DEFAUT: Record<Exclude<ApiErrorKind, "metier">, string> = {
  session_expiree: "Votre session a expiré. Reconnectez-vous.",
  acces_refuse: "Vous n'avez pas les droits nécessaires pour cette action.",
  validation: "La requête envoyée est invalide. Réessayez ou signalez le problème si ça persiste.",
  limite_atteinte: "Trop de tentatives. Réessayez plus tard.",
  serveur: "Une erreur technique est survenue côté serveur. Réessayez dans un instant.",
  reseau: "Connexion au serveur impossible. Vérifiez votre réseau et réessayez.",
};

interface OptionsErreur {
  /** Route d'authentification (login) : un 401 y signifie "identifiants invalides", pas "session expirée". */
  authRoute?: boolean;
}

/**
 * Classe la réponse d'erreur du backend, qui prend deux formes distinctes :
 * `{code, message}` pour les erreurs métier (DomainError), `{detail}` pour tout le
 * reste (401 d'authentification, 422 de validation Pydantic natif, 429, 5xx non
 * intercepté) — voir application_fastapi.py pour le handler `{code,message}`.
 */
export async function throwIfError(response: Response, options: OptionsErreur = {}): Promise<void> {
  if (response.ok) return;
  const body = await response.json().catch(() => null);

  if (typeof body?.code === "string" && typeof body?.message === "string") {
    throw new ApiError("metier", body.code, response.status, body.message, body.details);
  }

  if (response.status === 401 && !options.authRoute) {
    throw new ApiError(
      "session_expiree",
      "session_expiree",
      401,
      MESSAGE_PAR_DEFAUT.session_expiree
    );
  }

  if (response.status === 403) {
    throw new ApiError("acces_refuse", "acces_refuse", 403, MESSAGE_PAR_DEFAUT.acces_refuse);
  }

  if (response.status === 429) {
    const message =
      typeof body?.detail === "string" ? body.detail : MESSAGE_PAR_DEFAUT.limite_atteinte;
    throw new ApiError("limite_atteinte", "limite_atteinte", 429, message);
  }

  if (Array.isArray(body?.detail)) {
    throw new ApiError(
      "validation",
      "validation_invalide",
      response.status,
      MESSAGE_PAR_DEFAUT.validation,
      body.detail
    );
  }

  if (typeof body?.detail === "string") {
    throw new ApiError("serveur", "erreur_serveur", response.status, body.detail);
  }

  throw new ApiError("serveur", "erreur_serveur", response.status, MESSAGE_PAR_DEFAUT.serveur);
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
  options?: OptionsErreur
): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(input, init);
  } catch {
    throw new ApiError("reseau", "connexion_impossible", 0, MESSAGE_PAR_DEFAUT.reseau);
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
    (error: unknown, repli: string): void => {
      if (error instanceof ApiError && error.kind === "session_expiree") {
        toast.error("Votre session a expiré. Vous allez être redirigé vers la connexion.");
        const chemin = encodeURIComponent(window.location.pathname);
        router.push(`/connexion?redirect=${chemin}`);
        return;
      }
      toast.error(error instanceof ApiError ? error.message : repli);
    },
    [router]
  );
}
