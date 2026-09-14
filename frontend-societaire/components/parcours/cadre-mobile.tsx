import Image from "next/image";

/**
 * Habillage desktop d'un parcours pensé mobile. En dessous de `sm` (640px),
 * transparent : le contenu garde exactement le rendu plein écran déjà validé
 * (ancré en haut, compact). À partir de `sm`, deux colonnes plein écran — panneau
 * de marque à gauche, formulaire à droite (pattern d'onboarding desktop standard :
 * Stripe, Linear...) — plutôt qu'une petite carte perdue au milieu d'un fond vide,
 * qui donnait une impression inachevée sur un grand écran. Pertinent en particulier
 * parce que la démo tournera probablement sur un ordinateur portable.
 */
export function CadreMobile({ children }: { children: React.ReactNode }) {
  return (
    <div className="sm:flex sm:min-h-dvh">
      <div className="hidden shrink-0 flex-col items-center justify-center gap-6 bg-solida-teal-800 px-12 text-center sm:flex sm:w-2/5 sm:min-h-dvh lg:w-1/2">
        <Image
          src="/solida-logo.png"
          alt="SOLIDA"
          width={72}
          height={54}
          className="brightness-0 invert"
        />
        <p className="max-w-xs text-balance font-serif-title text-xl text-blanc">
          Faites votre demande de crédit simplement, depuis chez vous.
        </p>
      </div>

      <div className="sm:flex sm:min-h-dvh sm:flex-1 sm:items-center sm:justify-center sm:overflow-y-auto sm:bg-neutre-50 sm:px-10 sm:py-10">
        <div className="sm:w-full sm:max-w-md">{children}</div>
      </div>
    </div>
  );
}
