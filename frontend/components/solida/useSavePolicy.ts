import { useState } from "react";
import { toast } from "sonner";
import type { ConfigurationGrilleApi } from "@/lib/contracts";
import { ApiError, throwIfError } from "@/lib/services/error-service";

interface ParametresPolitique {
  marge: number;
  lgd: number;
  multiplicateurAccord: number;
  multiplicateurExamen: number;
  plafondsProduits: Record<string, number>;
}

export function useSavePolicy(
  configurationInitiale: ConfigurationGrilleApi,
  autoriseAModifier: boolean
) {
  const [version, setVersion] = useState(configurationInitiale.version_grille);
  const [enregistrementEnCours, setEnregistrementEnCours] = useState(false);

  async function enregistrer(parametres: ParametresPolitique) {
    if (!autoriseAModifier) return;
    setEnregistrementEnCours(true);
    const [major, minor] = version.replace(/^v/, "").split(".").map(Number);
    const nouvelleVersion = `v${major}.${(minor ?? 0) + 1}`;
    const {
      pdo,
      score_reference: scoreReference,
      odds_reference: oddsReference,
    } = configurationInitiale.scorecard;
    try {
      const reponse = await fetch("/api/v1/parametrage/grille", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          version_grille: nouvelleVersion,
          grille: {
            marge: parametres.marge,
            lgd: parametres.lgd,
            multiplicateur_accord: parametres.multiplicateurAccord,
            multiplicateur_vigilance: configurationInitiale.grille.multiplicateur_vigilance,
            multiplicateur_examen: parametres.multiplicateurExamen,
          },
          progressif: {
            ...configurationInitiale.progressif,
            plafonds_produits: parametres.plafondsProduits,
          },
          scorecard: { pdo, score_reference: scoreReference, odds_reference: oddsReference },
        }),
      });
      await throwIfError(reponse);
      setVersion(nouvelleVersion);
      toast.success(`Politique de crédit ${nouvelleVersion} enregistrée`);
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "L'enregistrement a échoué.");
    } finally {
      setEnregistrementEnCours(false);
    }
  }

  return { version, enregistrementEnCours, enregistrer };
}
