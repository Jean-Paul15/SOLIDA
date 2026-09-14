import { useRouter } from "next/navigation";
import * as React from "react";

/**
 * Garde-fou de navigation partagé par les écrans du parcours qui exigent une valeur de contexte
 * déjà enregistrée (jeton de session, numéro de compte) : redirige vers le point d'entrée du
 * parcours si elle est absente, et indique à l'appelant s'il peut rendre l'écran.
 */
export function useEtapeProtegee<T>(
  valeur: T,
  redirectionVers: string = "/numero-compte",
): boolean {
  const router = useRouter();

  React.useEffect(() => {
    if (!valeur) router.replace(redirectionVers);
  }, [valeur, router, redirectionVers]);

  return Boolean(valeur);
}
