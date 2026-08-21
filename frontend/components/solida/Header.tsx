"use client";

import { Loader2, LogOut } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { canAccessCreditPolicy } from "@/lib/roles";

interface HeaderProps {
  agence?: string | null;
  userName?: string;
  role?: string;
}

export function Header({ agence, userName, role }: HeaderProps) {
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);

  async function logOut() {
    setLoggingOut(true);
    // Meme filet que le formulaire de connexion : sans try/catch, une requete qui echoue
    // avant d'atteindre le serveur laissait le bouton bloque en chargement indefiniment,
    // sans jamais rediriger vers l'ecran de connexion.
    try {
      await fetch("/api/v1/auth/logout", { method: "POST" });
    } catch {
      // Rien a afficher : on redirige quand meme vers /connexion, ou une session encore
      // active cote serveur redemandera simplement les identifiants au prochain appel.
    } finally {
      router.push("/connexion");
      setLoggingOut(false);
    }
  }

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-neutre-200 bg-blanc px-6">
      <div className="flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2">
          <Image src="/solida-logo.png" alt="SOLIDA" width={32} height={24} priority />
          <span className="font-serif-title text-base font-semibold text-solida-teal-900">
            SOLIDA
          </span>
        </Link>
        {userName && (
          <nav className="flex items-center gap-4 text-sm text-neutre-700">
            <Link href="/registre" className="hover:text-neutre-950">
              Registre
            </Link>
            {canAccessCreditPolicy(role) && (
              <Link href="/parametrage/grille" className="hover:text-neutre-950">
                Politique de crédit
              </Link>
            )}
          </nav>
        )}
      </div>
      <div className="flex items-center gap-4 text-sm text-neutre-700">
        {agence && <span>{agence}</span>}
        {userName && <span>{userName}</span>}
        <Button variant="ghost" size="sm" onClick={logOut} loading={loggingOut} className="gap-1.5">
          {loggingOut ? <Loader2 className="size-4 animate-spin" /> : <LogOut className="size-4" />}
          Se déconnecter
        </Button>
      </div>
    </header>
  );
}
