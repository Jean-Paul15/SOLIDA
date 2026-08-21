import { Skeleton } from "@/components/ui/skeleton";

/**
 * Affiché automatiquement par Next.js pendant la résolution du Server Component
 * `page.tsx` (fetch fiche + produits) : reproduit la forme finale (carte A4 de
 * `FicheApercu` + colonne d'actions de `FicheActions`). Le header reste affiché
 * sans interruption : il vit dans `layout.tsx`, pas ici.
 */
export default function ChargementFiche() {
  return (
    <>
      <div className="mx-auto w-full max-w-[1000px] px-6 pt-4">
        <Skeleton className="h-5 w-32" />
      </div>

      <main className="mx-auto flex w-full max-w-[1000px] flex-1 gap-6 px-6 py-6">
        <div className="flex-1">
          <Skeleton className="mx-auto aspect-[210/297] w-full max-w-[800px]" />
        </div>
        <div className="flex w-[220px] flex-col gap-2">
          <Skeleton className="h-9 w-full" />
          <Skeleton className="h-9 w-full" />
          <Skeleton className="h-9 w-full" />
        </div>
      </main>
    </>
  );
}
