import { Suspense } from "react";
import { FormulaireConnexion } from "@/components/solida/FormulaireConnexion";

export default function PageConnexion() {
  return (
    <div className="flex min-h-screen">
      <div className="hidden flex-col items-center justify-center gap-4 bg-solida-teal-900 px-12 text-center text-white lg:flex lg:w-[55%]">
        <h1 className="font-serif-title text-xl font-semibold">SOLIDA</h1>
        <p className="max-w-sm text-sm text-white/80">
          Scoring d&rsquo;octroi pour coopératives financières
        </p>
        <p className="absolute bottom-8 text-xs text-white/50">Programme DigiCoop-WA+</p>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center bg-blanc px-6">
        <div className="flex w-[360px] flex-col gap-6">
          <h2 className="font-serif-title text-xl font-semibold text-neutre-950">Connexion</h2>
          <Suspense>
            <FormulaireConnexion />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
