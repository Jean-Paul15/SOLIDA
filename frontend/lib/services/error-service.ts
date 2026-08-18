export class ApiError extends Error {
  readonly code: string;
  readonly details?: unknown;

  constructor(code: string, message: string, details?: unknown) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

export async function throwIfError(response: Response): Promise<void> {
  if (response.ok) return;
  const body = await response.json().catch(() => null);
  throw new ApiError(
    body?.code ?? "erreur_inconnue",
    body?.message ?? "Une erreur inattendue est survenue.",
    body?.details
  );
}
