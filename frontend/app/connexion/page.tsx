import { Suspense } from "react";
import { SavingsFlowBeam } from "@/components/solida/SavingsFlowBeam";
import { LoginForm } from "@/components/solida/LoginForm";
import { LogoAnime } from "@/components/solida/LogoAnime";

export default function PageConnexion() {
  return (
    <div className="flex min-h-screen">
      <div className="relative hidden flex-col items-center justify-center gap-4 overflow-hidden bg-solida-teal-900 px-12 text-center text-white lg:flex lg:w-[55%]">
        <SavingsFlowBeam />
        <LogoAnime />
        <p className="max-w-lg text-2xl leading-relaxed text-white/85">
          L&rsquo;épargne d&rsquo;aujourd&rsquo;hui trace le crédit de demain.
        </p>
        <div className="absolute bottom-8 flex flex-col items-center gap-1 text-sm text-white/50">
          <p>Programme DigiCoop-WA+</p>
          <p className="font-serif-title italic">
            CIF — « Faire autrement ensemble pour rendre les futurs possibles ! »
          </p>
        </div>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center bg-blanc px-6">
        <div className="flex w-[360px] flex-col gap-6">
          <h2 className="font-serif-title text-xl font-semibold text-neutre-950">Connexion</h2>
          <Suspense>
            <LoginForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
