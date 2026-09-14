import { ArrowRight } from "lucide-react";

interface ConditionsReexamenProps {
  conditions: string[];
  /** Fiche PDF : texte plus petit, limité aux 3 premières conditions. */
  compact?: boolean;
}

/** Rendu partagé entre l'écran de résultat et la fiche de justification : un même levier de
 * réexamen se présente pareil aux deux endroits (cohérence du pattern, pas de duplication). */
export function ConditionsReexamen({ conditions, compact = false }: ConditionsReexamenProps) {
  const items = compact ? conditions.slice(0, 3) : conditions;
  return (
    <ul className={`flex flex-col gap-1.5 ${compact ? "text-[11px]" : "text-sm"} text-neutre-700`}>
      {items.map((condition) => (
        <li key={condition} className="flex items-start gap-1.5">
          <ArrowRight
            className={`shrink-0 text-solida-teal-600 ${compact ? "mt-0.5 size-3" : "mt-0.5 size-3.5"}`}
            aria-hidden="true"
          />
          <span>{condition}</span>
        </li>
      ))}
    </ul>
  );
}
