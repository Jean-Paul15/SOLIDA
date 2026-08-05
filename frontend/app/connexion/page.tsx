import Image from "next/image";
import { Suspense } from "react";
import { FluxEpargneBeam } from "@/components/solida/FluxEpargneBeam";
import { FormulaireConnexion } from "@/components/solida/FormulaireConnexion";

export default function PageConnexion() {
  return (
    <div className="flex min-h-screen">
      <div className="relative hidden flex-col items-center justify-center gap-4 overflow-hidden bg-solida-teal-900 px-12 text-center text-white lg:flex lg:w-[55%]">
        <FluxEpargneBeam />
        <Image
          src="/solida-logo.png"
          alt="SOLIDA"
          width={220}
          height={168}
          priority
          className="relative"
        />
        <p className="max-w-lg text-2xl leading-relaxed text-white/85">
          L&rsquo;épargne d&rsquo;aujourd&rsquo;hui trace le crédit de demain.
        </p>
        <p className="absolute bottom-8 text-sm text-white/50">Programme DigiCoop-WA+</p>
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
