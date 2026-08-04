"use client";

import { LogOut } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

interface EnTeteProps {
  agence?: string;
  utilisateur?: string;
}

export function EnTete({ agence, utilisateur }: EnTeteProps) {
  const router = useRouter();

  async function seDeconnecter() {
    await fetch("/api/v1/auth/deconnexion", { method: "POST" });
    router.push("/connexion");
  }

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-neutre-200 bg-blanc px-6">
      <Link href="/" className="flex items-center gap-2">
        <Image src="/solida-logo.png" alt="SOLIDA" width={32} height={24} priority />
        <span className="font-serif-title text-base font-semibold text-solida-teal-900">
          SOLIDA
        </span>
      </Link>
      <div className="flex items-center gap-4 text-sm text-neutre-700">
        {agence && <span>{agence}</span>}
        {utilisateur && <span>{utilisateur}</span>}
        <Button variant="ghost" size="sm" onClick={seDeconnecter} className="gap-1.5">
          <LogOut className="size-4" />
          Se déconnecter
        </Button>
      </div>
    </header>
  );
}
