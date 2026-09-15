import { LogoAnime } from "./logo-anime";
import { SavingsFlowBeam } from "./savings-flow-beam";

/**
 * Habillage desktop d'un parcours pensé mobile. En dessous de `sm` (640px),
 * transparent : le contenu garde exactement le rendu plein écran déjà validé
 * (ancré en haut, compact). À partir de `sm`, deux colonnes plein écran — panneau
 * de marque à gauche, formulaire à droite (pattern d'onboarding desktop standard :
 * Stripe, Linear...) — plutôt qu'une petite carte perdue au milieu d'un fond vide,
 * qui donnait une impression inachevée sur un grand écran. Pertinent en particulier
 * parce que la démo tournera probablement sur un ordinateur portable.
 *
 * Panneau de marque identique à l'écran de connexion agent
 * (frontend/app/connexion/page.tsx) : même fond, même fond animé (SavingsFlowBeam),
 * même logo flottant (LogoAnime), même bandeau de bas de panneau — pour qu'un agent
 * qui bascule de son propre écran de connexion à une démonstration du portail
 * sociétaire retrouve la même identité visuelle, pas deux styles différents pour
 * la même marque.
 */
export function CadreMobile({ children }: { children: React.ReactNode }) {
  return (
    <div className="sm:flex sm:min-h-dvh">
      <div className="relative hidden shrink-0 flex-col items-center justify-center gap-4 overflow-hidden bg-solida-teal-900 px-12 text-center sm:flex sm:w-2/5 sm:min-h-dvh lg:w-[55%]">
        <SavingsFlowBeam />
        <LogoAnime />
        <p className="max-w-lg text-balance font-serif-title text-xl leading-relaxed text-blanc/85">
          Faites votre demande de crédit simplement, depuis chez vous.
        </p>
        <div className="absolute bottom-8 flex flex-col items-center gap-1 text-sm text-blanc/50">
          <p>Programme DigiCoop-WA+</p>
          <p className="font-serif-title italic">
            CIF — « Faire autrement ensemble pour rendre les futurs possibles ! »
          </p>
        </div>
      </div>

      <div className="sm:flex sm:min-h-dvh sm:flex-1 sm:items-center sm:justify-center sm:overflow-y-auto sm:bg-neutre-50 sm:px-10 sm:py-10">
        <div className="sm:w-full sm:max-w-md">{children}</div>
      </div>
    </div>
  );
}
