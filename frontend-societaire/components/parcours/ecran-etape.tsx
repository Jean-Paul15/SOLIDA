"use client";

import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { CadreMobile } from "./cadre-mobile";
import { cn } from "@/lib/utils";

const NB_ETAPES = 7;

/**
 * Coquille commune aux écrans de saisie du parcours ("Étape 3 sur 7", section 5 du
 * document — l'estimation facultative de la situation économique a ajouté une étape à
 * l'origine à 6 ; le choix du produit, ajouté puis retiré, est désormais déduit du
 * segment du sociétaire). Un seul bouton d'action visible par écran (section 3), retour
 * toujours possible (section 5 : "aucune impasse").
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
    <CadreMobile>
      {/* Pas de flex-1 ici : le bouton suit le contenu de près, il n'est pas plaqué
          en bas d'un écran vide sur les étapes courtes (C2, C3, C7...). sm:min-h-0
          neutralise min-h-dvh une fois dans la carte desktop (CadreMobile) : sinon
          le contenu forcerait la carte à occuper toute la hauteur du viewport. */}
      <div className="mx-auto min-h-dvh max-w-md px-5 sm:min-h-0">
        {/* Sticky en haut, pas seulement le pied : le retour et la progression
            restent visibles même quand le contenu dépasse la hauteur de l'écran —
            section 5, "retour possible partout". */}
        <div className="sticky top-0 z-10 bg-background pt-5 pb-2">
          <header className="flex items-center gap-2.5">
            <button
              type="button"
              aria-label="Retour à l'étape précédente"
              onClick={() =>
                precedent ? router.push(precedent) : router.back()
              }
              className="flex size-9 shrink-0 items-center justify-center rounded-full text-foreground transition active:scale-90 hover:bg-muted active:bg-neutre-200"
            >
              <ChevronLeft className="size-5" />
            </button>
            <div className="flex flex-1 items-center gap-1.5" aria-hidden>
              {Array.from({ length: NB_ETAPES }, (_, i) => (
                <div
                  key={i}
                  className={cn(
                    "h-1.5 flex-1 rounded-full",
                    i < etape ? "bg-solida-teal-600" : "bg-neutre-200",
                  )}
                />
              ))}
            </div>
          </header>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Étape {etape} sur {NB_ETAPES}
          </p>
        </div>

        {/* Pousse le titre/champ vers la zone atteignable au pouce (bas-centre, pas
            le haut de l'écran — cf. recherche Steven Hoober / Smashing Magazine sur
            la "thumb zone") plutôt que de tout laisser collé sous l'en-tête. Un
            "clamp" plutôt qu'une valeur fixe : s'adapte à la hauteur réelle de
            l'écran sans jamais pousser trop loin sur un petit téléphone. Réinitialisé
            en desktop (sm:), où le panneau centre déjà le contenu correctement. */}
        <main className="mt-[clamp(2rem,12vh,5rem)] sm:mt-3">
          <h1 className="text-xl font-semibold text-balance">{titre}</h1>
          {sousTitre ? (
            <p className="mt-1.5 text-base text-muted-foreground">
              {sousTitre}
            </p>
          ) : null}
          <div className="mt-5">{children}</div>
        </main>

        {/* sticky (pas fixed) : suit le flux normal sur un écran court (aucun effet
            visible, le bouton reste juste après le contenu), et ne se pince en bas
            de son ancêtre défilant (le viewport en mobile, la carte en desktop) que
            si l'écran est assez long pour défiler (C6). */}
        <footer className="sticky bottom-0 mt-6 bg-background pt-2 pb-[max(1rem,env(safe-area-inset-bottom))]">
          {pied}
        </footer>
      </div>
    </CadreMobile>
  );
}
