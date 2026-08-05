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
import { formaterMontant } from "@/lib/format";
import type { SyntheseEpargne } from "@/lib/contracts";

const FLECHE_TENDANCE = {
  hausse: "↗ en hausse",
  stable: "→ stable",
  erosion: "↘ en érosion",
};

const JOUR_MS = 24 * 60 * 60 * 1000;
const DOUZE_MOIS_MS = 365 * JOUR_MS;
const HORIZONS = [3, 6, 9, 12] as const;

export function MouvementsEpargne({ epargne }: { epargne: SyntheseEpargne }) {
  const [maintenant] = useState(() => Date.now());
  const [horizonMois, setHorizonMois] = useState<number>(12);
  const debutFenetre = maintenant - DOUZE_MOIS_MS;
  const debutHorizon = maintenant - (horizonMois / 12) * DOUZE_MOIS_MS;

  // Solde cumulé des mouvements réels connus sur 12 mois, ancré sur le solde moyen (6 mois) :
  // pas une reconstruction fabriquée, seulement les points réellement observés reliés entre eux.
  const mouvementsTries = [...epargne.mouvements_recents]
    .filter((m) => new Date(m.date_operation).getTime() >= debutFenetre)
    .sort((a, b) => new Date(a.date_operation).getTime() - new Date(b.date_operation).getTime());

  // Le solde moyen (6 mois) ancre le point le plus récent ; chaque mouvement, en remontant
  // dans le temps, est retiré pour obtenir le solde juste avant lui.
  const pointsAsc = useMemo(() => {
    let cumul = epargne.solde_moyen_6m;
    const pointsDesc: { horodatage: number; solde: number }[] = [];
    for (let i = mouvementsTries.length - 1; i >= 0; i--) {
      const m = mouvementsTries[i];
      pointsDesc.push({ horodatage: new Date(m.date_operation).getTime(), solde: cumul });
      cumul -= m.sens === "depot" ? m.montant : -m.montant;
    }
    return pointsDesc.reverse();
    // mouvementsTries recree a chaque rendu (filter/sort) : comparer sur la longueur suffit,
    // le contenu de epargne ne change pas sans un nouveau rendu du dossier.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [epargne.solde_moyen_6m, mouvementsTries.length]);

  const dansHorizon = pointsAsc.filter((p) => p.horodatage >= debutHorizon);
  const avantHorizon = pointsAsc.filter((p) => p.horodatage < debutHorizon);
  const soldeAuDebut = avantHorizon[avantHorizon.length - 1]?.solde ?? epargne.solde_moyen_6m;
  const soldeActuel = pointsAsc[pointsAsc.length - 1]?.solde ?? epargne.solde_moyen_6m;
  const donnees = [
    { horodatage: debutHorizon, solde: soldeAuDebut },
    ...dansHorizon,
    { horodatage: maintenant, solde: soldeActuel },
  ];

  const moisRemplis = Array.from({ length: 12 }, (_, i) => i < epargne.nb_mois_avec_depot_12m);

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-neutre-500">Trajectoire d&rsquo;épargne</span>
        <Select value={String(horizonMois)} onValueChange={(v) => setHorizonMois(Number(v))}>
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
          {formaterMontant(epargne.solde_moyen_6m)}
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
            <XAxis dataKey="horodatage" type="number" domain={[debutHorizon, maintenant]} hide />
            <Tooltip
              labelFormatter={(v) => new Date(Number(v)).toLocaleDateString("fr-FR")}
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
        Dépôts effectués : {epargne.nb_mois_avec_depot_12m} mois sur 12
      </span>

      <span className="text-xs text-neutre-500">
        Sociétaire depuis {epargne.anciennete_relation_mois} mois, relation d&rsquo;épargne
        antérieure à toute demande de crédit.
      </span>
      {mouvementsTries.length > 0 && (
        <span className="text-xs text-neutre-400 italic">
          Courbe reconstruite à partir des mouvements réellement observés (échantillon), ancrée sur
          le solde moyen 6 mois.
        </span>
      )}
    </div>
  );
}
