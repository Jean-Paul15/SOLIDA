"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CadreMobile } from "@/components/parcours/cadre-mobile";

// Nom de la caisse : pas encore de source backend pour cette donnée (dette
// documentée, cf. plan). Variable d'environnement en attendant, jamais une valeur
// d'institution réelle codée en dur dans l'app.
const NOM_CAISSE = process.env.NEXT_PUBLIC_NOM_CAISSE ?? "votre caisse";

export default function AccueilPage() {
  return (
    <CadreMobile>
      {/* pt en clamp (pas une valeur fixe) : pousse le bouton principal vers la
          zone atteignable au pouce en bas-centre plutôt que de tout laisser collé
          en haut, en s'adaptant à la hauteur réelle de l'écran. */}
      <div className="mx-auto flex min-h-dvh max-w-md flex-col items-center px-6 pt-[clamp(3rem,15vh,6rem)] text-center sm:min-h-0 sm:py-12">
        <div className="flex size-16 items-center justify-center rounded-full bg-solida-teal-50">
          <Image src="/solida-logo.png" alt="SOLIDA" width={36} height={27} priority />
        </div>
        <h1 className="mt-5 text-xl font-semibold text-balance">Bienvenue à {NOM_CAISSE}</h1>
        <p className="mt-2 text-base text-muted-foreground text-balance">
          Faites une demande de crédit en quelques minutes, depuis votre téléphone.
        </p>

        <div className="mt-7 w-full">
          <Button asChild>
            <Link href="/numero-compte">Faire une demande</Link>
          </Button>
        </div>

        <p className="mt-6 text-sm text-muted-foreground">
          Vous préférez en parler directement ? Rendez-vous à votre agence habituelle.
        </p>
      </div>
    </CadreMobile>
  );
}
