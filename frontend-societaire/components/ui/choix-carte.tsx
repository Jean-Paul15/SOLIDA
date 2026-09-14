"use client";

import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChoixCarteProps {
  selectionne: boolean;
  onClick: () => void;
  libelle: string;
  icone?: LucideIcon;
  /** "grille" : carte carrée avec icône centrée (ex. objet du crédit). "liste" : ligne pleine
   * largeur, texte aligné à gauche (ex. durée). */
  disposition?: "grille" | "liste";
}

/** Carte sélectionnable partagée par les écrans à choix unique (objet, durée) : même style de
 * sélection, une seule définition à faire évoluer. */
export function ChoixCarte({
  selectionne,
  onClick,
  libelle,
  icone: Icone,
  disposition = "liste",
}: ChoixCarteProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={selectionne}
      className={cn(
        "rounded-lg border-2 font-medium transition",
        disposition === "grille"
          ? "flex min-h-22 flex-col items-center justify-center gap-1.5 px-3 py-3 text-center text-sm text-balance active:scale-[0.97]"
          : "min-h-12 px-4 text-left text-base active:scale-[0.98]",
        selectionne
          ? "border-solida-teal-600 bg-solida-teal-50 text-solida-teal-800"
          : "border-border bg-blanc text-foreground hover:bg-muted active:bg-neutre-100",
      )}
    >
      {Icone && <Icone className="size-5" strokeWidth={1.75} />}
      <span>{libelle}</span>
    </button>
  );
}
