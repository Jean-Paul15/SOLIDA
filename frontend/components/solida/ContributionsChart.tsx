"use client";

import { useState } from "react";
import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ContributionVariable } from "@/lib/contracts";

const LIMITE_VISIBLE = 8;

export function ContributionsChart({ decomposition }: { decomposition: ContributionVariable[] }) {
  const [allVisible, setAllVisible] = useState(false);

  if (decomposition.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-neutre-500 italic">
        Aucune contribution significative identifiée pour ce dossier.
      </p>
    );
  }

  const visibles = allVisible ? decomposition : decomposition.slice(0, LIMITE_VISIBLE);
  const masques = decomposition.length - LIMITE_VISIBLE;

  const chartData = visibles.map((contribution) => ({
    nom: `${contribution.libelle} : ${contribution.valeur}`,
    points: contribution.points,
    sens: contribution.sens,
  }));

  const amplitude = Math.max(...decomposition.map((c) => Math.abs(c.points)), 1);

  return (
    <div className="flex flex-col gap-3">
      <div style={{ height: visibles.length * 38 + 20 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ left: 4, right: 28 }}
            barCategoryGap={14}
          >
            <XAxis type="number" domain={[-amplitude, amplitude]} hide />
            <YAxis
              type="category"
              dataKey="nom"
              width={220}
              tick={{ fontSize: 13, fill: "var(--color-neutre-700)" }}
              axisLine={false}
              tickLine={false}
            />
            <ReferenceLine x={0} stroke="var(--color-neutre-300)" />
            <Tooltip
              contentStyle={{
                borderRadius: 6,
                borderColor: "var(--color-neutre-200)",
                fontSize: 12,
              }}
              formatter={(v) => {
                const n = Math.round(Number(v));
                return n > 0 ? `+${n}` : n;
              }}
            />
            <Bar dataKey="points" barSize={26} animationDuration={200} isAnimationActive>
              {chartData.map((datum) => (
                <Cell
                  key={datum.nom}
                  fill={
                    datum.sens === "favorable"
                      ? "var(--color-decision-accord)"
                      : datum.sens === "defavorable"
                        ? "var(--color-decision-refus)"
                        : "var(--color-neutre-500)"
                  }
                  fillOpacity={0.85}
                />
              ))}
              <LabelList
                dataKey="points"
                position="right"
                formatter={(v) => {
                  const n = Math.round(Number(v));
                  return n > 0 ? `+${n}` : String(n);
                }}
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 12,
                  fill: "var(--color-neutre-950)",
                }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center gap-4 text-xs text-neutre-500">
        <span className="flex items-center gap-1.5">
          <span className="size-2.5 rounded-full bg-decision-accord" />
          Favorable au score
        </span>
        <span className="flex items-center gap-1.5">
          <span className="size-2.5 rounded-full bg-decision-refus" />
          Défavorable au score
        </span>
      </div>

      {masques > 0 && (
        <button
          type="button"
          onClick={() => setAllVisible((v) => !v)}
          className="cursor-pointer self-start text-xs text-solida-teal-800 underline"
        >
          {allVisible ? "Réduire" : `+ ${masques} autres facteurs`}
        </button>
      )}
    </div>
  );
}
