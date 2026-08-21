"use client";

import { useMemo, useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { formatAmount } from "@/lib/format";
import type { SyntheseEpargne } from "@/lib/contracts";
import { savingsTrajectory } from "@/lib/savings-trajectory";

const FLECHE_TENDANCE = {
  hausse: "↗ en hausse",
  stable: "→ stable",
  erosion: "↘ en érosion",
};

// Les 4 horizons agrègent les mouvements réels par mois calendaire (net dépôts - retraits),
// jamais un point par mouvement brut. La courbe et les puces de régularité sont recalculées sur
// exactement les mêmes données mensuelles : un mois marqué avec dépôt allume toujours sa puce et
// produit toujours la hausse de solde correspondante (voir simulateur/simulateur/pipeline.py,
// gen_epargne, qui aligne désormais les mouvements générés sur les mois "avec dépôt" plutôt que
// sur un échantillon aléatoire décorrélé).
const HORIZONS = [3, 6, 9, 12] as const;

export function SavingsMovements({ epargne }: { epargne: SyntheseEpargne }) {
  const [maintenant] = useState(() => Date.now());
  const [monthsHorizon, setMonthsHorizon] = useState<number>(12);

  const donnees = useMemo(
    () => savingsTrajectory(epargne, monthsHorizon, maintenant),
    [epargne, monthsHorizon, maintenant]
  );

  const nbMoisAvecDepot = donnees.filter((d) => d.depots > 0).length;
  const moisRemplis = donnees.map((d) => d.depots > 0);

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-neutre-500">Trajectoire d&rsquo;épargne</span>
        <Select value={String(monthsHorizon)} onValueChange={(v) => setMonthsHorizon(Number(v))}>
          <SelectTrigger size="sm" className="w-auto gap-1 border-none text-xs shadow-none">
            <SelectValue />
          </SelectTrigger>
          <SelectContent align="end">
            {HORIZONS.map((h) => (
              <SelectItem key={h} value={String(h)} className="text-xs">
                {h} mois
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-baseline gap-2">
        <span className="font-mono text-lg text-neutre-950">
          {formatAmount(epargne.solde_moyen_6m)}
        </span>
        <span className="text-xs text-neutre-500">{FLECHE_TENDANCE[epargne.tendance_12m]}</span>
      </div>

      <div className="h-[120px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={donnees} margin={{ top: 4, right: 4, bottom: 0, left: 4 }}>
            <defs>
              <linearGradient id="degradeSolde" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--color-solida-teal-700)" stopOpacity={0.18} />
                <stop offset="100%" stopColor="var(--color-solida-teal-700)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="horodatage" type="category" hide />
            <Tooltip
              labelFormatter={(v) =>
                new Date(Number(v)).toLocaleDateString("fr-FR", { month: "long", year: "numeric" })
              }
              formatter={(_valeur, _nom, item) => {
                const { depots, retraits } = item.payload as { depots: number; retraits: number };
                if (depots === 0 && retraits === 0) return ["Aucun mouvement enregistré", ""];
                return [`Dépôts ${formatAmount(depots)} · Retraits ${formatAmount(retraits)}`, ""];
              }}
              labelClassName="text-xs"
              contentStyle={{
                borderRadius: 6,
                borderColor: "var(--color-neutre-200)",
                fontSize: 12,
              }}
            />
            <Area
              type="monotone"
              dataKey="solde"
              stroke="var(--color-solida-teal-700)"
              strokeWidth={1.5}
              fill="url(#degradeSolde)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="flex gap-1">
        {moisRemplis.map((remplit, i) => (
          <div
            key={i}
            className={
              remplit
                ? "size-3.5 rounded-sm bg-solida-teal-600"
                : "size-3.5 rounded-sm border border-neutre-300"
            }
          />
        ))}
      </div>
      <span className="text-xs text-neutre-500">
        Régularité d&rsquo;épargne : {nbMoisAvecDepot}/{monthsHorizon} mois avec dépôt
      </span>

      <span className="text-xs text-neutre-500">
        Mouvements réels observés sur les {monthsHorizon} derniers mois.
      </span>

      <span className="text-xs text-neutre-500">
        Sociétaire depuis {epargne.anciennete_relation_mois} mois, relation d&rsquo;épargne
        antérieure à toute demande de crédit.
      </span>
    </div>
  );
}
