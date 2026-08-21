import { User, Users } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { NumberTicker } from "@/components/solida/NumberTicker";
import type { ScoringResult } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";
import { TRANCHE_COLOR, LABEL_TRANCHE } from "@/lib/labels";
import {
  FOND_TRANCHE_JAUGE,
  gaugePosition,
  SCORE_MAX,
  SCORE_MIN,
  gaugeSegments,
  type Zones,
} from "@/lib/score-gauge";

interface RecommendationPanelProps {
  result: ScoringResult;
  zones: Zones | null;
}

export function RecommendationPanel({ result, zones }: RecommendationPanelProps) {
  const couleurs = TRANCHE_COLOR[result.tranche];
  const positionScore = gaugePosition(result.score);

  return (
    <div className="flex h-full flex-col gap-4">
      <div
        className={`flex flex-col gap-3 rounded-lg border-l-3 ${couleurs.border} ${couleurs.background} p-4`}
      >
        <span className="text-sm text-neutre-700">Recommandation</span>
        <NumberTicker valeur={result.score} className="font-mono text-score text-neutre-950" />
        <span className="text-xs text-neutre-500">points sur 850</span>

        <div className="flex flex-col gap-1">
          <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-neutre-200">
            {zones &&
              gaugeSegments(zones).map((s) => (
                <Tooltip key={s.tranche}>
                  <TooltipTrigger asChild>
                    <div
                      className={`absolute top-0 h-full cursor-help ${FOND_TRANCHE_JAUGE[s.tranche]}`}
                      style={{ left: `${s.gauche}%`, width: `${s.droite - s.gauche}%` }}
                    />
                  </TooltipTrigger>
                  <TooltipContent>
                    {LABEL_TRANCHE[s.tranche]} : {s.legende}
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
                  style={{ left: `${gaugePosition(zones.scoreExamen)}%` }}
                />
                <span
                  className="absolute top-1 -translate-x-1/2 font-mono text-[10px] text-neutre-500"
                  style={{ left: `${gaugePosition(zones.scoreExamen)}%` }}
                >
                  {Math.round(zones.scoreExamen)}
                </span>
                <div
                  className="absolute top-0 h-1 w-px -translate-x-1/2 bg-neutre-300"
                  style={{ left: `${gaugePosition(zones.scoreAccord)}%` }}
                />
                <span
                  className="absolute top-1 -translate-x-1/2 font-mono text-[10px] text-neutre-500"
                  style={{ left: `${gaugePosition(zones.scoreAccord)}%` }}
                >
                  {Math.round(zones.scoreAccord)}
                </span>
              </>
            )}
          </div>
        </div>

        <span className={`text-lg font-semibold ${couleurs.text}`}>
          {LABEL_TRANCHE[result.tranche]}
        </span>

        {result.tranche !== "refus" && (
          <div>
            <span className="text-sm text-neutre-500">Montant recommandé</span>
            <div className="font-mono text-lg text-neutre-950">
              {formatAmount(result.montant_recommande)}
            </div>
            <span className="text-xs text-neutre-500">
              sur {formatAmount(result.montant_demande)} sollicités
            </span>
          </div>
        )}

        <span className="text-xs text-neutre-500">
          La décision finale relève de l&rsquo;agent et du comité de crédit.
        </span>
      </div>

      <div className="flex items-center gap-2 text-xs text-neutre-700">
        {result.mode_calcul === "enrichi" ? (
          <>
            <Users className="size-4" />
            Score calculé avec l&rsquo;historique du groupe de caution (segment groupement).
          </>
        ) : (
          <>
            <User className="size-4" />
            Score calculé sur le profil individuel et l&rsquo;épargne : la garantie de ce crédit est
            l&rsquo;épargne nantie.
          </>
        )}
      </div>

      {result.avertissements.map((a) => (
        <Alert key={a}>
          <AlertDescription>{a}</AlertDescription>
        </Alert>
      ))}

      <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
        <span className="text-xs font-medium text-neutre-500">Palier suivant accessible</span>
        {result.trajectoire_progression.map((p) => (
          <div key={p.cycle} className="flex justify-between text-sm">
            <span className="text-neutre-700">Prochain cycle</span>
            <span className="font-mono text-neutre-950">{formatAmount(p.plafond_accessible)}</span>
          </div>
        ))}
        <span className="text-xs text-neutre-500 italic">
          Estimation à profil de risque inchangé, non contractuelle : réévaluée au moment du
          renouvellement.
        </span>
      </div>
    </div>
  );
}
