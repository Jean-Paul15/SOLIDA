import { useEffect, useState } from "react";
import type { ConfigurationGrilleApi } from "@/lib/contracts";

/**
 * Fetch client de la grille active : ce composant est monté aussi bien depuis une page
 * server-rendue (résultat déjà enregistré) que depuis l'aperçu de prévisualisation
 * (pas encore de route serveur dédiée) — incohérence connue avec le reste des pages,
 * qui font toutes leur fetch côté serveur, à corriger si une route serveur commune
 * émerge pour ces deux cas.
 */
export function useConfigurationGrille(): ConfigurationGrilleApi | null {
  const [configurationGrille, setConfigurationGrille] = useState<ConfigurationGrilleApi | null>(
    null
  );
  useEffect(() => {
    let annule = false;
    fetch("/api/v1/parametrage/grille")
      .then((r) => (r.ok ? r.json() : null))
      .then((c: ConfigurationGrilleApi | null) => {
        if (!annule) setConfigurationGrille(c);
      })
      .catch(() => {
        if (!annule) setConfigurationGrille(null);
      });
    return () => {
      annule = true;
    };
  }, []);

  return configurationGrille;
}
