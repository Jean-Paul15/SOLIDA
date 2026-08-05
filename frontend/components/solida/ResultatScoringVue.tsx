import { Loader2, User, Users } from "lucide-react";
import Link from "next/link";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { GraphiqueContributions } from "@/components/solida/GraphiqueContributions";
import { NumberTicker } from "@/components/solida/NumberTicker";
import type { ResultatScoring } from "@/lib/contracts";
import { formaterMontant } from "@/lib/format";
import { COULEUR_TRANCHE, LIBELLE_TRANCHE } from "@/lib/libelles";

const SCORE_MIN = 300;
const SCORE_MAX = 850;

interface ResultatScoringVueProps {
  resultat: ResultatScoring;
  /** Aperçu non encore enregistré : bascule les actions vers confirmer/annuler plutôt
   * que d'afficher les actions d'une décision déjà persistée (fiche, "enregistrée le"). */
  previsualisation?: boolean;
  surConfirmer?: () => void;
  surAnnuler?: () => void;
  confirmationEnCours?: boolean;
}

export function ResultatScoringVue({
  resultat,
  previsualisation = false,
  surConfirmer,
  surAnnuler,
  confirmationEnCours = false,
}: ResultatScoringVueProps) {
  const couleurs = COULEUR_TRANCHE[resultat.tranche];
  const positionScore = ((resultat.score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)) * 100;
  const sommeContributions = resultat.decomposition.reduce((s, c) => s + c.points, 0);

  return (
    <div className="mx-auto grid w-full max-w-[1440px] flex-1 grid-cols-12 gap-6 px-6 py-6">
      <div className="col-span-5 flex flex-col gap-4">
        <div
          className={`flex flex-col gap-3 rounded-lg border-l-3 ${couleurs.bordure} ${couleurs.fond} p-4`}
        >
          <span className="text-sm text-neutre-700">Recommandation</span>
          <NumberTicker valeur={resultat.score} className="font-mono text-score text-neutre-950" />
          <span className="text-xs text-neutre-500">points sur 850</span>

          <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-neutre-200">
            <div
              className="absolute top-0 h-full w-1 -translate-x-1/2 bg-neutre-950"
              style={{ left: `${positionScore}%` }}
            />
          </div>

          <span className={`text-lg font-semibold ${couleurs.texte}`}>
            {LIBELLE_TRANCHE[resultat.tranche]}
          </span>

          {resultat.tranche !== "refus" && (
            <div>
              <span className="text-sm text-neutre-500">Montant recommandé</span>
              <div className="font-mono text-lg text-neutre-950">
                {formaterMontant(resultat.montant_recommande)}
              </div>
              <span className="text-xs text-neutre-500">
                sur {formaterMontant(resultat.montant_demande)} sollicités
              </span>
            </div>
          )}

          <span className="text-xs text-neutre-500">
            La décision finale relève de l&rsquo;agent et du comité de crédit.
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs text-neutre-700">
          {resultat.mode_calcul === "enrichi" ? (
            <>
              <Users className="size-4" />
              Score calculé avec l&rsquo;historique du groupe de caution (segment groupement).
            </>
          ) : (
            <>
              <User className="size-4" />
              Score calculé sur le profil individuel et l&rsquo;épargne : la garantie de ce crédit
              est l&rsquo;épargne nantie.
            </>
          )}
        </div>

        {resultat.avertissements.map((a) => (
          <Alert key={a}>
            <AlertDescription>{a}</AlertDescription>
          </Alert>
        ))}

        <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">Trajectoire de progression</span>
          {resultat.trajectoire_progression.map((p) => (
            <div key={p.cycle} className="flex justify-between text-sm">
              <span className="text-neutre-700">Cycle +{p.cycle}</span>
              <span className="font-mono text-neutre-950">
                {formaterMontant(p.plafond_accessible)}
              </span>
            </div>
          ))}
        </div>

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
      </div>

      <div className="col-span-7 flex flex-col gap-4">
        <h2 className="font-serif-title text-lg font-semibold text-neutre-950">
          Facteurs déterminants
        </h2>
        <GraphiqueContributions decomposition={resultat.decomposition} />
        <span className="text-xs text-neutre-500">
          Base {Math.round(resultat.points_de_base)} + contributions{" "}
          {sommeContributions >= 0 ? "+" : ""}
          {Math.round(sommeContributions)} = {Math.round(resultat.score)}
        </span>

        <div className="mt-auto flex items-center justify-end gap-2">
          {previsualisation ? (
            <>
              <Button variant="outline" onClick={surAnnuler} disabled={confirmationEnCours}>
                Annuler
              </Button>
              <Button onClick={surConfirmer} disabled={confirmationEnCours}>
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
              <span className="mr-auto text-xs text-neutre-500">
                Décision enregistrée le{" "}
                {new Date(resultat.horodatage).toLocaleString("fr-FR", {
                  dateStyle: "long",
                  timeStyle: "short",
                })}
              </span>
              <Button variant="outline" asChild>
                <Link href="/">Nouvelle recherche</Link>
              </Button>
              <Button asChild>
                <Link href={`/scoring/${resultat.decision_id}/fiche`}>
                  Générer la fiche de justification
                </Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
