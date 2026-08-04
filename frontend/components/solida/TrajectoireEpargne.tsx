"use client";

import { Area, AreaChart, ResponsiveContainer, Tooltip } from "recharts";
import { formaterMontant } from "@/lib/format";
import type { SyntheseEpargne } from "@/lib/contracts";

const FLECHE_TENDANCE = {
  hausse: "↗ en hausse",
  stable: "→ stable",
  erosion: "↘ en érosion",
};

export function TrajectoireEpargne({ epargne }: { epargne: SyntheseEpargne }) {
  const donnees = epargne.serie_solde_12m.map((p) => ({
    mois: new Date(p.mois).toLocaleDateString("fr-FR", { month: "short" }),
    solde: p.solde,
  }));

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
      <span className="text-xs font-medium text-neutre-500">Trajectoire d&rsquo;épargne</span>

      <div className="flex items-baseline gap-2">
        <span className="font-mono text-lg text-neutre-950">
          {formaterMontant(epargne.solde_moyen_6m)}
        </span>
        <span className="text-xs text-neutre-500">{FLECHE_TENDANCE[epargne.tendance_12m]}</span>
      </div>

      <div className="h-[120px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={donnees} margin={{ top: 4, right: 4, bottom: 0, left: 4 }}>
            <defs>
              <linearGradient id="degradeSolde" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--color-solida-teal-700)" stopOpacity={0.08} />
                <stop offset="100%" stopColor="var(--color-solida-teal-700)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Tooltip
              formatter={(valeur) => formaterMontant(Number(valeur))}
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
        {epargne.serie_solde_12m.map((p, i) => (
          <div
            key={p.mois}
            className={
              i < epargne.nb_mois_avec_depot_12m
                ? "size-3.5 rounded-sm bg-solida-teal-600"
                : "size-3.5 rounded-sm border border-neutre-300"
            }
            title={p.mois}
          />
        ))}
      </div>
      <span className="text-xs text-neutre-500">
        Dépôts effectués : {epargne.nb_mois_avec_depot_12m} mois sur 12
      </span>

      <span className="text-xs text-neutre-500">
        Sociétaire depuis {epargne.anciennete_relation_mois} mois — relation d&rsquo;épargne
        antérieure à toute demande de crédit.
      </span>
    </div>
  );
}
