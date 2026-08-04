export class ErreurService extends Error {
  readonly code: string;
  readonly details?: unknown;

  constructor(code: string, message: string, details?: unknown) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

export async function leverSiEnErreur(reponse: Response): Promise<void> {
  if (reponse.ok) return;
  const corps = await reponse.json().catch(() => null);
  throw new ErreurService(
    corps?.code ?? "erreur_inconnue",
    corps?.message ?? "Une erreur inattendue est survenue.",
    corps?.details
  );
}
