"use client";

import { Loader2, LogOut } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";

interface EnTeteProps {
  agence?: string;
  utilisateur?: string;
}

export function EnTete({ agence, utilisateur }: EnTeteProps) {
  const router = useRouter();
  const [deconnexionEnCours, setDeconnexionEnCours] = useState(false);

  async function seDeconnecter() {
    setDeconnexionEnCours(true);
    await fetch("/api/v1/auth/deconnexion", { method: "POST" });
    router.push("/connexion");
  }

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-neutre-200 bg-blanc px-6">
      <div className="flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2">
          <Image src="/solida-logo.png" alt="SOLIDA" width={32} height={24} priority />
          <span className="font-serif-title text-base font-semibold text-solida-teal-900">
            SOLIDA
          </span>
        </Link>
        {utilisateur && (
          <nav className="flex items-center gap-4 text-sm text-neutre-700">
            <Link href="/registre" className="hover:text-neutre-950">
              Registre
            </Link>
            <Link href="/parametrage/grille" className="hover:text-neutre-950">
              Grille
            </Link>
          </nav>
        )}
      </div>
      <div className="flex items-center gap-4 text-sm text-neutre-700">
        {agence && <span>{agence}</span>}
        {utilisateur && <span>{utilisateur}</span>}
        <Button
          variant="ghost"
          size="sm"
          onClick={seDeconnecter}
          disabled={deconnexionEnCours}
          className="gap-1.5"
        >
          {deconnexionEnCours ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <LogOut className="size-4" />
          )}
          Se déconnecter
        </Button>
      </div>
    </header>
  );
}
