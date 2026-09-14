import { useState } from "react";
import { ApiError } from "@/lib/services/error-service";

interface RunOptions {
  /** Affiché (et renvoyé à `onError`) si l'erreur n'est pas une `ApiError` porteuse de son
   * propre message. */
  fallbackErrorMessage?: string;
  onError?: (error: unknown, message: string) => void;
}

/** Distingue un échec d'un succès dont la valeur de retour est `undefined` (ex. une action qui
 * ne renvoie rien) : `undefined` seul ne suffit pas à le faire. */
export const ECHEC = Symbol("echec-async-action");

/**
 * Centralise le triplet `inProgress`/`error`/`try-catch-finally` répété à l'identique autour
 * de chaque appel API déclenché par un clic (nouvelle demande, confirmation, archivage) : ce
 * hook ne remplace ni `useApiErrorToast` (affichage) ni `withMinDuration` (lissage du temps de
 * chargement perçu), il élimine seulement la triplication du state autour d'eux.
 */
export function useAsyncAction() {
  const [inProgress, setInProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run<T>(action: () => Promise<T>, options?: RunOptions): Promise<T | typeof ECHEC> {
    setInProgress(true);
    setError(null);
    try {
      return await action();
    } catch (e) {
      const message =
        e instanceof ApiError
          ? e.message
          : (options?.fallbackErrorMessage ?? "Une erreur est survenue.");
      setError(message);
      options?.onError?.(e, message);
      return ECHEC;
    } finally {
      setInProgress(false);
    }
  }

  function reset(): void {
    setError(null);
  }

  return { inProgress, error, run, reset };
}
