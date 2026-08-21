import { AlertTriangle } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { ActiviteEconomique } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";

interface EconomicActivityPanelProps {
  activite: ActiviteEconomique;
}

export function EconomicActivityPanel({ activite }: EconomicActivityPanelProps) {
  return (
    <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
      <span className="text-xs font-medium text-neutre-500">Activité économique</span>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <span className="text-neutre-500">Secteur</span>
        <span className="text-neutre-950">{activite.secteur}</span>
        <span className="text-neutre-500">Ancienneté de l&rsquo;activité</span>
        <span className="text-neutre-950">
          {Math.floor(activite.anciennete_activite_mois / 12)} an(s)
        </span>
        <span className="text-neutre-500">Revenu mensuel déclaré</span>
        {activite.revenu_mensuel_declare ? (
          <span className="font-mono text-neutre-950">
            {formatAmount(activite.revenu_mensuel_declare)}
          </span>
        ) : (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-1 text-sm text-neutre-500 italic">
                Non renseigné <AlertTriangle className="size-3.5 text-alerte" />
              </span>
            </TooltipTrigger>
            <TooltipContent>
              Ce champ est absent du dossier et sera imputé lors du scoring, ce qui réduit la
              précision.
            </TooltipContent>
          </Tooltip>
        )}
        <span className="text-neutre-500">Capacité de remboursement estimée</span>
        <span className="font-mono text-neutre-950">
          {formatAmount(activite.capacite_remboursement_estimee)}
        </span>
      </div>
    </div>
  );
}
