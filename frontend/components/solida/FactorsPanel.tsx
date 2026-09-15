import { Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ConditionsReexamen } from "@/components/solida/ConditionsReexamen";
import { ContributionsChart } from "@/components/solida/ContributionsChart";
import type { ScoringResult } from "@/lib/contracts";

interface FactorsPanelProps {
  result: ScoringResult;
  isPreview: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmationInProgress: boolean;
  /** Consultation par un rôle qui ne tranche pas (superviseur) : ni confirmer/annuler
   * (ce n'est pas son rôle), ni les actions d'une décision persistée (cette demande n'est
   * pas encore une décision enregistrée, seulement un aperçu produit par le portail). */
  readOnly?: boolean;
}

export function FactorsPanel({
  result,
  isPreview,
  onConfirm,
  onCancel,
  confirmationInProgress,
  readOnly = false,
}: FactorsPanelProps) {
  const sommeContributions = result.decomposition.reduce((s, c) => s + c.points, 0);

  return (
    <div className="flex h-full flex-col gap-4">
      <h2 className="font-serif-title text-lg font-semibold text-neutre-950">
        Facteurs déterminants
      </h2>
      <ContributionsChart decomposition={result.decomposition} />
      <span className="text-xs text-neutre-500">
        Score de base du modèle : {Math.round(result.points_de_base)} pts. Ajustement total des
        facteurs ci-dessus : {sommeContributions >= 0 ? "+" : ""}
        {Math.round(sommeContributions)} pts. Score final : {Math.round(result.score)} pts.
      </span>
      <span className="text-xs text-neutre-500">
        Modèle {result.version_modele} · Grille {result.version_grille}
      </span>

      {result.conditions_reexamen.length > 0 && (
        <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">
            {result.tranche === "accord"
              ? "Recommandations pour consolider le profil"
              : "Conditions de réexamen"}
          </span>
          <ConditionsReexamen conditions={result.conditions_reexamen} />
        </div>
      )}

      <div className="mt-auto flex flex-col gap-2">
        {readOnly ? (
          <span className="text-xs text-neutre-500">
            Vue en lecture seule : l&rsquo;agent assigné confirmera ou non cette décision.
          </span>
        ) : (
          <>
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
          </>
        )}
      </div>
    </div>
  );
}
