import { Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ContributionsChart } from "@/components/solida/ContributionsChart";
import type { ScoringResult } from "@/lib/contracts";

interface FactorsPanelProps {
  result: ScoringResult;
  isPreview: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmationInProgress: boolean;
}

export function FactorsPanel({
  result,
  isPreview,
  onConfirm,
  onCancel,
  confirmationInProgress,
}: FactorsPanelProps) {
  const sommeContributions = result.decomposition.reduce((s, c) => s + c.points, 0);

  return (
    <div className="flex h-full flex-col gap-4">
      <h2 className="font-serif-title text-lg font-semibold text-neutre-950">
        Facteurs déterminants
      </h2>
      <ContributionsChart decomposition={result.decomposition} />
      <span className="text-xs text-neutre-500">
        Base {Math.round(result.points_de_base)} + contributions{" "}
        {sommeContributions >= 0 ? "+" : ""}
        {Math.round(sommeContributions)} = {Math.round(result.score)}
      </span>
      <span className="text-xs text-neutre-500">
        Modèle {result.version_modele} · Grille {result.version_grille}
      </span>

      {result.tranche !== "accord" && result.conditions_reexamen.length > 0 && (
        <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">Conditions de réexamen</span>
          <ul className="list-disc pl-4 text-sm text-neutre-700">
            {result.conditions_reexamen.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-auto flex flex-col gap-2">
        <div className="flex items-center gap-2">
          {isPreview ? (
            <>
              <Button
                variant="outline"
                onClick={onCancel}
                loading={confirmationInProgress}
                className="flex-1"
              >
                Annuler
              </Button>
              <Button onClick={onConfirm} loading={confirmationInProgress} className="flex-1">
                {confirmationInProgress ? (
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
                <Link href={`/scoring/${result.decision_id}/fiche`}>
                  Générer la fiche de justification
                </Link>
              </Button>
            </>
          )}
        </div>
        {!isPreview && (
          <span className="text-xs text-neutre-500">
            Décision enregistrée le{" "}
            {new Date(result.horodatage).toLocaleString("fr-FR", {
              dateStyle: "long",
              timeStyle: "short",
            })}
          </span>
        )}
      </div>
    </div>
  );
}
