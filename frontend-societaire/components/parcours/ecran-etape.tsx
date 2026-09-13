"use client";

import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { cn } from "@/lib/utils";

const NB_ETAPES = 6;

/**
 * Coquille commune aux écrans C2 à C7 (les 6 étapes de saisie — "Étape 3 sur 6",
 * section 5 du document). Un seul bouton d'action visible par écran (section 3),
 * retour toujours possible (section 5 : "aucune impasse").
 */
export function EcranEtape({
  etape,
  titre,
  sousTitre,
  children,
  pied,
  precedent,
}: {
  etape: number;
  titre: string;
  sousTitre?: string;
  children: React.ReactNode;
  pied: React.ReactNode;
  /** Chemin de retour explicite ; sans lui, retour navigateur standard. */
  precedent?: string;
}) {
  const router = useRouter();

  return (
    <div className="mx-auto flex min-h-dvh max-w-md flex-col px-5">
      {/* Sticky en haut, pas seulement le pied : le retour et la progression restent
          visibles même quand le contenu (ex. la grille d'objets, C6) dépasse la
          hauteur de l'écran — section 5, "retour possible partout". */}
      <div className="sticky top-0 z-10 bg-background pt-6 pb-2">
        <header className="flex items-center gap-3">
          <button
            type="button"
            aria-label="Retour à l'étape précédente"
            onClick={() => (precedent ? router.push(precedent) : router.back())}
            className="flex size-11 shrink-0 items-center justify-center rounded-full text-foreground hover:bg-muted active:bg-neutre-200"
          >
            <ChevronLeft className="size-6" />
          </button>
          <div className="flex flex-1 items-center gap-1.5" aria-hidden>
            {Array.from({ length: NB_ETAPES }, (_, i) => (
              <div
                key={i}
                className={cn(
                  "h-1.5 flex-1 rounded-full",
                  i < etape ? "bg-solida-teal-600" : "bg-neutre-200"
                )}
              />
            ))}
          </div>
        </header>
        <p className="mt-2 text-sm text-muted-foreground">
          Étape {etape} sur {NB_ETAPES}
        </p>
      </div>

      <main className="mt-4 flex flex-1 flex-col">
        <h1 className="text-xl font-semibold text-balance">{titre}</h1>
        {sousTitre ? <p className="mt-2 text-base text-muted-foreground">{sousTitre}</p> : null}
        <div className="mt-8 flex-1">{children}</div>
      </main>

      <footer className="sticky bottom-0 mt-6 bg-background pt-2 pb-[env(safe-area-inset-bottom)]">
        {pied}
      </footer>
    </div>
  );
}
