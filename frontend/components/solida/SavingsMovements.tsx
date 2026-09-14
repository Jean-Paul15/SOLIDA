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
import { selectHorizon } from "@/lib/savings-trajectory";

const TREND_LABEL = {
  hausse: "↗ en hausse",
  stable: "→ stable",
  erosion: "↘ en érosion",
};

// Fenêtre maximale proposée, jamais une garantie : jamais masquée même si l'historique réel
// est plus court (§5.14) — c'est `selectHorizon` qui sert l'intersection.
const HORIZONS = [3, 6, 9, 12] as const;

export function SavingsMovements({ epargne }: { epargne: SyntheseEpargne }) {
  const [monthsHorizon, setMonthsHorizon] = useState<number>(12);

  const chartData = useMemo(() => selectHorizon(epargne, monthsHorizon), [epargne, monthsHorizon]);
  const historiqueReduit = chartData.length < monthsHorizon;

  const depositMonths = chartData.filter((month) => month.depots > 0).length;
  const filledMonths = chartData.map((month) => month.depots > 0);

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
        <span className="text-xs text-neutre-500">{TREND_LABEL[epargne.tendance_12m]}</span>
      </div>

      <div className="h-[120px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: 4 }}>
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
        {filledMonths.map((isFilled, index) => (
          <div
            key={index}
            className={
              isFilled
                ? "size-3.5 rounded-sm bg-solida-teal-600"
                : "size-3.5 rounded-sm border border-neutre-300"
            }
          />
        ))}
      </div>
      <span className="text-xs text-neutre-500">
        Régularité d&rsquo;épargne : {depositMonths}/{chartData.length} mois avec dépôt
      </span>

      {historiqueReduit ? (
        <span className="text-xs font-medium text-alerte">
          Historique d&rsquo;épargne de {chartData.length} mois : indicateurs calculés sur une
          période réduite.
        </span>
      ) : (
        <span className="text-xs text-neutre-500">
          Mouvements réels observés sur les {chartData.length} derniers mois.
        </span>
      )}

      <span className="text-xs text-neutre-500">
        Sociétaire depuis {epargne.anciennete_relation_mois} mois, relation d&rsquo;épargne
        antérieure à toute demande de crédit.
      </span>
    </div>
  );
}
