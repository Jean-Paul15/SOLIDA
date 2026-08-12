"use client";

import { Loader2, User, Users } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { GraphiqueContributions } from "@/components/solida/GraphiqueContributions";
import { NumberTicker } from "@/components/solida/NumberTicker";
import type { ConfigurationGrilleApi, ResultatScoring, Tranche } from "@/lib/contracts";
import { formaterMontant } from "@/lib/format";
import { COULEUR_TRANCHE, LIBELLE_TRANCHE } from "@/lib/libelles";
import { scoreDepuisProbabilite, seuilEconomique } from "@/lib/scorecard";

const SCORE_MIN = 300;
const SCORE_MAX = 850;

const FOND_TRANCHE_JAUGE: Record<Tranche, string> = {
  refus: "bg-decision-refus",
  comite_de_credit: "bg-decision-comite",
  accord_sous_condition: "bg-decision-conditionnel",
  accord: "bg-decision-accord",
};

/** Convertit un score en position (%) sur la jauge [SCORE_MIN, SCORE_MAX]. */
function positionSurJauge(score: number): number {
  return Math.min(100, Math.max(0, ((score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)) * 100));
}

/**
 * Bornes de score des zones de la grille active, dérivées des mêmes formules que
 * l'écran de paramétrage (`PolitiqueCredit`) — pour qu'un score affiché ici et les
 * seuils affichés là-bas désignent toujours le même repère, sans calcul mental.
 * Note : la grille peut avoir été recalibrée depuis qu'une décision déjà enregistrée
 * a été prise ; ces bornes reflètent la grille active aujourd'hui, pas nécessairement
 * celle utilisée au moment exact de la décision (le score lui, oui).
 */
function bornesZones(configuration: ConfigurationGrilleApi) {
  const { grille, scorecard } = configuration;
  const parametresScorecard = {
    pdo: scorecard.pdo,
    scoreReference: scorecard.score_reference,
    oddsReference: scorecard.odds_reference,
  };
  const seuil = seuilEconomique({
    marge: grille.marge,
    lgd: grille.lgd,
    multiplicateurAccord: grille.multiplicateur_accord,
    multiplicateurExamen: grille.multiplicateur_examen,
  });
  return {
    scoreAccord: scoreDepuisProbabilite(seuil * grille.multiplicateur_accord, parametresScorecard),
    scoreVigilance: scoreDepuisProbabilite(seuil, parametresScorecard),
    scoreExamen: scoreDepuisProbabilite(seuil * grille.multiplicateur_examen, parametresScorecard),
  };
}

type Zones = ReturnType<typeof bornesZones>;

/** Les 4 tranches de la jauge, bornes et légende de survol, dans l'ordre score croissant. */
function segmentsJauge(zones: Zones) {
  const arrondi = (n: number) => Math.round(n);
  return [
    {
      tranche: "refus" as const,
      gauche: 0,
      droite: positionSurJauge(zones.scoreExamen),
      legende: `score < ${arrondi(zones.scoreExamen)}`,
    },
    {
      tranche: "comite_de_credit" as const,
      gauche: positionSurJauge(zones.scoreExamen),
      droite: positionSurJauge(zones.scoreVigilance),
      legende: `score ${arrondi(zones.scoreExamen)} à ${arrondi(zones.scoreVigilance)}`,
    },
    {
      tranche: "accord_sous_condition" as const,
      gauche: positionSurJauge(zones.scoreVigilance),
      droite: positionSurJauge(zones.scoreAccord),
      legende: `score ${arrondi(zones.scoreVigilance)} à ${arrondi(zones.scoreAccord)}`,
    },
    {
      tranche: "accord" as const,
      gauche: positionSurJauge(zones.scoreAccord),
      droite: 100,
      legende: `score ≥ ${arrondi(zones.scoreAccord)}`,
    },
  ];
}

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
  const positionScore = positionSurJauge(resultat.score);
  const sommeContributions = resultat.decomposition.reduce((s, c) => s + c.points, 0);

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

  const zones = useMemo(
    () => (configurationGrille ? bornesZones(configurationGrille) : null),
    [configurationGrille]
  );

  return (
    <div className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-6 px-6 py-6">
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-5 flex flex-col gap-4">
          <div
            className={`flex flex-col gap-3 rounded-lg border-l-3 ${couleurs.bordure} ${couleurs.fond} p-4`}
          >
            <span className="text-sm text-neutre-700">Recommandation</span>
            <NumberTicker
              valeur={resultat.score}
              className="font-mono text-score text-neutre-950"
            />
            <span className="text-xs text-neutre-500">points sur 850</span>

            <div className="flex flex-col gap-1">
              <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-neutre-200">
                {zones &&
                  segmentsJauge(zones).map((s) => (
                    <Tooltip key={s.tranche}>
                      <TooltipTrigger asChild>
                        <div
                          className={`absolute top-0 h-full cursor-help ${FOND_TRANCHE_JAUGE[s.tranche]}`}
                          style={{ left: `${s.gauche}%`, width: `${s.droite - s.gauche}%` }}
                        />
                      </TooltipTrigger>
                      <TooltipContent>
                        {LIBELLE_TRANCHE[s.tranche]} : {s.legende}
                      </TooltipContent>
                    </Tooltip>
                  ))}
                <div
                  className="absolute top-0 h-full w-1 -translate-x-1/2 border border-blanc bg-neutre-950"
                  style={{ left: `${positionScore}%` }}
                />
              </div>
              <div className="relative h-4">
                <span className="absolute left-0 font-mono text-[10px] text-neutre-500/70">
                  {SCORE_MIN}
                </span>
                <span className="absolute right-0 font-mono text-[10px] text-neutre-500/70">
                  {SCORE_MAX}
                </span>
                {zones && (
                  <>
                    <div
                      className="absolute top-0 h-1 w-px -translate-x-1/2 bg-neutre-300"
                      style={{ left: `${positionSurJauge(zones.scoreExamen)}%` }}
                    />
                    <span
                      className="absolute top-1 -translate-x-1/2 font-mono text-[10px] text-neutre-500"
                      style={{ left: `${positionSurJauge(zones.scoreExamen)}%` }}
                    >
                      {Math.round(zones.scoreExamen)}
                    </span>
                    <div
                      className="absolute top-0 h-1 w-px -translate-x-1/2 bg-neutre-300"
                      style={{ left: `${positionSurJauge(zones.scoreAccord)}%` }}
                    />
                    <span
                      className="absolute top-1 -translate-x-1/2 font-mono text-[10px] text-neutre-500"
                      style={{ left: `${positionSurJauge(zones.scoreAccord)}%` }}
                    >
                      {Math.round(zones.scoreAccord)}
                    </span>
                  </>
                )}
              </div>
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
            <span className="text-xs font-medium text-neutre-500">Palier suivant accessible</span>
            {resultat.trajectoire_progression.map((p) => (
              <div key={p.cycle} className="flex justify-between text-sm">
                <span className="text-neutre-700">Prochain cycle</span>
                <span className="font-mono text-neutre-950">
                  {formaterMontant(p.plafond_accessible)}
                </span>
              </div>
            ))}
            <span className="text-xs text-neutre-500 italic">
              Estimation à profil de risque inchangé, non contractuelle : réévaluée au moment du
              renouvellement.
            </span>
          </div>
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
                    onClick={surAnnuler}
                    disabled={confirmationEnCours}
                    className="flex-1"
                  >
                    Annuler
                  </Button>
                  <Button onClick={surConfirmer} disabled={confirmationEnCours} className="flex-1">
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
      </div>
    </div>
  );
}
