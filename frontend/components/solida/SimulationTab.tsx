import { Section } from "@/components/solida/Section";
import { LABEL_TRANCHE } from "@/lib/labels";

interface SimulationTabProps {
  total: number;
  compte: (tranche: string) => number;
  tauxApprobation: number;
}

export function SimulationTab({ total, compte, tauxApprobation }: SimulationTabProps) {
  return (
    <div className="flex flex-col gap-3">
      <Section
        title="Simulation sur portefeuille de démonstration"
        description="Recalculée en direct à partir des réglages de l'onglet Seuils."
      />
      <div className="rounded-lg border border-alerte/40 bg-alerte/10 p-3 text-xs text-neutre-700">
        Résultats fournis à titre d&rsquo;exemple, non représentatifs du portefeuille réel.
      </div>
      <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
        <span className="text-xs font-medium text-neutre-500">
          Répartition sur {total} dossiers
        </span>
        {(["accord", "accord_sous_condition", "comite_de_credit", "refus"] as const).map((t) => (
          <div key={t} className="flex items-center gap-3">
            <span className="w-40 text-sm text-neutre-700">{LABEL_TRANCHE[t]}</span>
            <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-neutre-200">
              <div
                className="absolute h-full bg-solida-teal-600"
                style={{ width: `${total > 0 ? (compte(t) / total) * 100 : 0}%` }}
              />
            </div>
            <span className="w-10 text-right font-mono text-sm text-neutre-950">{compte(t)}</span>
          </div>
        ))}
        <span className="text-xs text-neutre-500">
          Taux d&rsquo;approbation : {(tauxApprobation * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}
