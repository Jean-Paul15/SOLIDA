import { Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { GraphiqueContributions } from "@/components/solida/GraphiqueContributions";
import type { ResultatScoring } from "@/lib/contracts";

interface PanneauFacteursProps {
  resultat: ResultatScoring;
  previsualisation: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmationEnCours: boolean;
}

export function PanneauFacteurs({
  resultat,
  previsualisation,
  onConfirm,
  onCancel,
  confirmationEnCours,
}: PanneauFacteursProps) {
  const sommeContributions = resultat.decomposition.reduce((s, c) => s + c.points, 0);

  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-serif-title text-lg font-semibold text-neutre-950">
        Facteurs déterminants
      </h2>
      <GraphiqueContributions decomposition={resultat.decomposition} />
      <span className="text-xs text-neutre-500">
        Base {Math.round(resultat.points_de_base)} + contributions{" "}
        {sommeContributions >= 0 ? "+" : ""}
        {Math.round(sommeContributions)} = {Math.round(resultat.score)}
      </span>
      <span className="text-xs text-neutre-500">
        Modèle {resultat.version_modele} · Grille {resultat.version_grille}
      </span>

      {resultat.tranche !== "accord" && resultat.conditions_reexamen.length > 0 && (
        <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">Conditions de réexamen</span>
          <ul className="list-disc pl-4 text-sm text-neutre-700">
            {resultat.conditions_reexamen.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-auto flex flex-col gap-2">
        <div className="flex items-center gap-2">
          {previsualisation ? (
            <>
              <Button
                variant="outline"
                onClick={onCancel}
                disabled={confirmationEnCours}
                className="flex-1"
              >
                Annuler
              </Button>
              <Button onClick={onConfirm} disabled={confirmationEnCours} className="flex-1">
                {confirmationEnCours ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    Enregistrement…
                  </>
                ) : (
                  "Enregistrer la décision"
                )}
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" asChild className="flex-1">
                <Link href="/">Nouvelle recherche</Link>
              </Button>
              <Button asChild className="flex-1">
                <Link href={`/scoring/${resultat.decision_id}/fiche`}>
                  Générer la fiche de justification
                </Link>
              </Button>
            </>
          )}
        </div>
        {!previsualisation && (
          <span className="text-xs text-neutre-500">
            Décision enregistrée le{" "}
            {new Date(resultat.horodatage).toLocaleString("fr-FR", {
              dateStyle: "long",
              timeStyle: "short",
            })}
          </span>
        )}
      </div>
    </div>
  );
}
