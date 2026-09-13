"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { LISTE_OBJETS_CREDIT, OBJETS_CREDIT, type ObjetCredit } from "@/lib/objets-credit";
import { cn } from "@/lib/utils";

export default function ObjetPage() {
  const router = useRouter();
  const { jetonSession, objet, enregistrerObjet } = useDemande();
  const [selection, setSelection] = React.useState<ObjetCredit | null>(objet);

  React.useEffect(() => {
    if (!jetonSession) router.replace("/numero-compte");
  }, [jetonSession, router]);

  if (!jetonSession) return null;

  function continuer() {
    if (!selection) return;
    enregistrerObjet(selection);
    router.push("/duree");
  }

  return (
    <EcranEtape
      etape={5}
      titre="Pour quoi faire ?"
      pied={
        <Button onClick={continuer} disabled={!selection}>
          Continuer
        </Button>
      }
    >
      <div className="grid grid-cols-2 gap-3">
        {LISTE_OBJETS_CREDIT.map((cle) => {
          const { libelle, icone: Icone } = OBJETS_CREDIT[cle];
          const active = selection === cle;
          return (
            <button
              key={cle}
              type="button"
              onClick={() => setSelection(cle)}
              aria-pressed={active}
              className={cn(
                "flex min-h-28 flex-col items-center justify-center gap-2 rounded-lg border-2 px-3 py-4 text-center transition-colors",
                active
                  ? "border-solida-teal-600 bg-solida-teal-50 text-solida-teal-800"
                  : "border-border bg-blanc text-foreground hover:bg-muted"
              )}
            >
              <Icone className="size-7" strokeWidth={1.75} />
              <span className="text-sm font-medium text-balance">{libelle}</span>
            </button>
          );
        })}
      </div>
    </EcranEtape>
  );
}
