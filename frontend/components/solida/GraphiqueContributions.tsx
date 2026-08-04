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

export function GraphiqueContributions({
  decomposition,
}: {
  decomposition: ContributionVariable[];
}) {
  const [tousVisibles, setTousVisibles] = useState(false);
  const visibles = tousVisibles ? decomposition : decomposition.slice(0, LIMITE_VISIBLE);
  const masques = decomposition.length - visibles.length;

  const donnees = visibles.map((c) => ({
    nom: `${c.libelle} : ${c.valeur}`,
    points: c.points,
    sens: c.sens,
  }));

  const amplitude = Math.max(...decomposition.map((c) => Math.abs(c.points)), 1);

  return (
    <div className="flex flex-col gap-2">
      <div style={{ height: visibles.length * 30 + 20 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={donnees}
            layout="vertical"
            margin={{ left: 4, right: 24 }}
            barCategoryGap={10}
          >
            <XAxis type="number" domain={[-amplitude, amplitude]} hide />
            <YAxis
              type="category"
              dataKey="nom"
              width={220}
              tick={{ fontSize: 12, fill: "var(--color-neutre-700)" }}
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
                const n = Number(v);
                return n > 0 ? `+${n}` : n;
              }}
            />
            <Bar dataKey="points" barSize={20} animationDuration={200} isAnimationActive>
              {donnees.map((d) => (
                <Cell
                  key={d.nom}
                  fill={
                    d.sens === "favorable"
                      ? "var(--color-decision-accord)"
                      : d.sens === "defavorable"
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
                  const n = Number(v);
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

      {!tousVisibles && masques > 0 && (
        <button
          type="button"
          onClick={() => setTousVisibles(true)}
          className="cursor-pointer self-start text-xs text-solida-teal-800 underline"
        >
          + {masques} autres facteurs
        </button>
      )}
    </div>
  );
}
