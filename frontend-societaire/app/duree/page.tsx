"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import type { DureeMois } from "@/lib/contracts";
import { cn } from "@/lib/utils";

const CHOIX: { valeur: DureeMois; libelle: string }[] = [
  { valeur: 3, libelle: "3 mois" },
  { valeur: 6, libelle: "6 mois" },
  { valeur: 12, libelle: "12 mois" },
  { valeur: 24, libelle: "24 mois" },
];

export default function DureePage() {
  const router = useRouter();
  const { jetonSession, dureeMois, enregistrerDuree } = useDemande();
  const [selection, setSelection] = React.useState<DureeMois | null>(dureeMois);

  React.useEffect(() => {
    if (!jetonSession) router.replace("/numero-compte");
  }, [jetonSession, router]);

  if (!jetonSession) return null;

  function continuer() {
    if (!selection) return;
    enregistrerDuree(selection);
    router.push("/recapitulatif");
  }

  return (
    <EcranEtape
      etape={6}
      titre="Sur combien de temps ?"
      pied={
        <Button onClick={continuer} disabled={!selection}>
          Continuer
        </Button>
      }
    >
      <div className="flex flex-col gap-2">
        {CHOIX.map(({ valeur, libelle }) => {
          const selectionne = selection === valeur;
          return (
            <button
              key={valeur}
              type="button"
              onClick={() => setSelection(valeur)}
              aria-pressed={selectionne}
              className={cn(
                "min-h-12 rounded-lg border-2 px-4 text-left text-base font-medium transition active:scale-[0.98]",
                selectionne
                  ? "border-solida-teal-600 bg-solida-teal-50 text-solida-teal-800"
                  : "border-border bg-blanc text-foreground hover:bg-muted active:bg-neutre-100"
              )}
            >
              {libelle}
            </button>
          );
        })}
      </div>
    </EcranEtape>
  );
}
