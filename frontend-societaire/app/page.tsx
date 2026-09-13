"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

// Nom de la caisse : pas encore de source backend pour cette donnée (dette
// documentée, cf. plan). Variable d'environnement en attendant, jamais une valeur
// d'institution réelle codée en dur dans l'app.
const NOM_CAISSE = process.env.NEXT_PUBLIC_NOM_CAISSE ?? "votre caisse";

export default function AccueilPage() {
  return (
    <div className="mx-auto flex min-h-dvh max-w-md flex-col items-center justify-center px-6 py-10 text-center">
      <div className="flex size-20 items-center justify-center rounded-full bg-solida-teal-50">
        <span className="font-serif-title text-3xl text-solida-teal-800" aria-hidden>
          S
        </span>
      </div>
      <h1 className="mt-6 text-2xl font-semibold text-balance">Bienvenue à {NOM_CAISSE}</h1>
      <p className="mt-3 text-base text-muted-foreground text-balance">
        Faites une demande de crédit en quelques minutes, depuis votre téléphone.
      </p>

      <div className="mt-10 w-full">
        <Button asChild>
          <Link href="/numero-compte">Faire une demande</Link>
        </Button>
      </div>

      <p className="mt-8 text-sm text-muted-foreground">
        Vous préférez en parler directement ? Rendez-vous à votre agence habituelle.
      </p>
    </div>
  );
}
