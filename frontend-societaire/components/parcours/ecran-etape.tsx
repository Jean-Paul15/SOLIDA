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
    // Pas de min-h-dvh/flex-1 ici : le bouton suit le contenu de près, il n'est pas
    // plaqué en bas d'un écran vide sur les étapes courtes (C2, C3, C7...). Le
    // wrapper ne prend que la hauteur de son contenu ; sur un écran long (C6, la
    // grille d'objets), la page défile normalement.
    <div className="mx-auto min-h-dvh max-w-md px-5">
      {/* Sticky en haut, pas seulement le pied : le retour et la progression restent
          visibles même quand le contenu dépasse la hauteur de l'écran — section 5,
          "retour possible partout". */}
      <div className="sticky top-0 z-10 bg-background pt-5 pb-2">
        <header className="flex items-center gap-2.5">
          <button
            type="button"
            aria-label="Retour à l'étape précédente"
            onClick={() => (precedent ? router.push(precedent) : router.back())}
            className="flex size-9 shrink-0 items-center justify-center rounded-full text-foreground hover:bg-muted active:bg-neutre-200"
          >
            <ChevronLeft className="size-5" />
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
        <p className="mt-1.5 text-sm text-muted-foreground">
          Étape {etape} sur {NB_ETAPES}
        </p>
      </div>

      <main className="mt-3">
        <h1 className="text-xl font-semibold text-balance">{titre}</h1>
        {sousTitre ? <p className="mt-1.5 text-base text-muted-foreground">{sousTitre}</p> : null}
        <div className="mt-5">{children}</div>
      </main>

      {/* sticky (pas fixed) : suit le flux normal sur un écran court (aucun effet
          visible, le bouton reste juste après le contenu), et ne se pince en bas du
          viewport que si l'écran est assez long pour défiler (C6) — ça évite de
          forcer une hauteur mini artificielle tout en gardant le bouton atteignable
          sur les écrans à contenu long. */}
      <footer className="sticky bottom-0 mt-6 bg-background pt-2 pb-[max(1rem,env(safe-area-inset-bottom))]">
        {pied}
      </footer>
    </div>
  );
}
