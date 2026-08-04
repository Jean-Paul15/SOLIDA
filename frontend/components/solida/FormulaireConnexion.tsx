"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function FormulaireConnexion() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const identifiantRef = useRef<HTMLInputElement>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErreur(null);
    setEnCours(true);

    const formData = new FormData(event.currentTarget);
    const reponse = await fetch("/api/v1/auth/connexion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        identifiant: formData.get("identifiant"),
        mot_de_passe: formData.get("mot_de_passe"),
      }),
    });

    if (!reponse.ok) {
      setEnCours(false);
      setErreur("Identifiant ou mot de passe incorrect.");
      identifiantRef.current?.focus();
      return;
    }

    router.push(searchParams.get("redirect") || "/");
  }

  return (
    <form onSubmit={onSubmit} className="flex w-full flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="identifiant">Identifiant</Label>
        <Input
          ref={identifiantRef}
          id="identifiant"
          name="identifiant"
          autoFocus
          autoComplete="username"
          disabled={enCours}
          required
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="mot_de_passe">Mot de passe</Label>
        <Input
          id="mot_de_passe"
          name="mot_de_passe"
          type="password"
          autoComplete="current-password"
          disabled={enCours}
          required
        />
      </div>
      {erreur && (
        <p role="alert" className="text-sm text-decision-refus">
          {erreur}
        </p>
      )}
      <Button type="submit" disabled={enCours} className="w-full">
        {enCours ? "Connexion…" : "Se connecter"}
      </Button>
    </form>
  );
}
