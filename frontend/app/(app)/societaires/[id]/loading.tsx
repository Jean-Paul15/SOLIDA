import { Skeleton } from "@/components/ui/skeleton";

/**
 * Affiché automatiquement par Next.js pendant la résolution du Server Component
 * `page.tsx` (fetch dossier + produits) : reproduit la forme finale du dossier 360°
 * (bandeau identité, grille 5/4/3 Profil+Activité / Trajectoire d'épargne / Groupe
 * de caution, puis historique de crédit). Le header reste affiché sans
 * interruption : il vit dans `layout.tsx`, pas ici.
 */
export default function ChargementDossier() {
  return (
    <main className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-6 px-6 py-6">
      <Skeleton className="h-5 w-40" />

      <div className="flex h-[88px] items-center rounded-lg border border-neutre-200 px-4">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-3 w-64" />
          <Skeleton className="h-3 w-40" />
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-5 flex flex-col gap-4">
          <Skeleton className="h-40 w-full rounded-lg" />
          <Skeleton className="h-32 w-full rounded-lg" />
        </div>
        <div className="col-span-4">
          <Skeleton className="h-72 w-full rounded-lg" />
        </div>
        <div className="col-span-3">
          <Skeleton className="h-56 w-full rounded-lg" />
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <Skeleton className="h-3 w-32" />
        <Skeleton className="h-40 w-full rounded-lg" />
      </div>
    </main>
  );
}
