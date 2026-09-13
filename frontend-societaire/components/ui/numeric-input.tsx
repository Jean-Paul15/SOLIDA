import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Champ numérique unique pour ce parcours : grand, clavier chiffres uniquement
 * (`inputMode="numeric"`), pas de saisie libre. Utilisé pour C2 (numéro de compte)
 * et C3 (montant du dernier dépôt) — section 3 de SOLIDA_Flux_Societaire.md.
 */
function NumericInput({ className, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type="text"
      inputMode="numeric"
      pattern="[0-9]*"
      autoComplete="off"
      data-slot="numeric-input"
      className={cn(
        "h-16 w-full min-w-0 rounded-lg border-2 border-input bg-blanc px-4 text-center font-mono text-2xl tracking-widest text-foreground transition-colors outline-none placeholder:text-muted-foreground/60 focus-visible:border-solida-teal-600 disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-4 aria-invalid:ring-destructive/20",
        className
      )}
      {...props}
    />
  );
}

export { NumericInput };
