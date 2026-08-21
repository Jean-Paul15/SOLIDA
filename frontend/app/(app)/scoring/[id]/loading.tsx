import { Skeleton } from "@/components/ui/skeleton";

/**
 * Affiché automatiquement par Next.js pendant la résolution du Server Component
 * `page.tsx` (fetch scoring + dossier) : reproduit la forme finale de
 * `ScoringResultView` (grille 5/7, Recommandation à gauche, Facteurs à droite). Le
 * header reste affiché sans interruption : il vit dans `layout.tsx`, pas ici.
 */
export default function ChargementResultatScoring() {
  return (
    <div className="mx-auto w-full max-w-[1440px] px-6 pt-4">
      <Skeleton className="h-5 w-40" />

      <div className="mt-6 grid grid-cols-12 gap-6">
        <div className="col-span-5 flex flex-col gap-4">
          <div className="flex flex-col gap-3 rounded-lg border-l-3 border-neutre-200 p-4">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-14 w-40" />
            <Skeleton className="h-2.5 w-full rounded-full" />
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-10 w-full" />
          </div>
          <Skeleton className="h-20 w-full rounded-lg" />
        </div>

        <div className="col-span-7 flex flex-col gap-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-48 w-full rounded-lg" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
          <div className="mt-auto flex gap-2">
            <Skeleton className="h-9 flex-1" />
            <Skeleton className="h-9 flex-1" />
          </div>
        </div>
      </div>
    </div>
  );
}
