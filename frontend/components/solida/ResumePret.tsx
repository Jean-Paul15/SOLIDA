import { formaterMontant } from "@/lib/format";

interface ResumePretProps {
  echeance: number;
  tauxEndettement: number;
}

export function ResumePret({ echeance, tauxEndettement }: ResumePretProps) {
  return (
    <div className="flex flex-col gap-1 border-t border-neutre-200 pt-4">
      <div className="flex justify-between text-sm">
        <span className="text-neutre-500">Échéance mensuelle estimée</span>
        <span className="font-mono text-neutre-950">{formaterMontant(echeance)}</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-neutre-500">Taux d&rsquo;endettement résultant</span>
        <span
          className={tauxEndettement > 0.7 ? "font-mono text-alerte" : "font-mono text-neutre-950"}
        >
          {tauxEndettement.toFixed(2)}
        </span>
      </div>
    </div>
  );
}
