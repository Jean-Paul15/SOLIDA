"use client";

import { Eye, EyeOff } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ReponseConnexionApi } from "@/lib/contracts";
import { safeRelativePath } from "@/lib/redirect";

export function FormulaireConnexion() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const identifiantRef = useRef<HTMLInputElement>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [motDePasseVisible, setMotDePasseVisible] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErreur(null);
    setEnCours(true);

    const formData = new FormData(event.currentTarget);
    // Delai d'abandon + try/catch : sans ca, une requete qui echoue avant meme d'atteindre
    // le serveur (reseau coupe momentanement) ou qui ne repond jamais laissait le bouton
    // bloque sur "Connexion..." indefiniment, sans autre issue que de recharger la page.
    const controleur = new AbortController();
    const delaiAbandon = setTimeout(() => controleur.abort(), 15_000);
    try {
      const reponse = await fetch("/api/v1/auth/connexion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifiant: formData.get("identifiant"),
          mot_de_passe: formData.get("mot_de_passe"),
        }),
        signal: controleur.signal,
      });

      if (!reponse.ok) {
        setErreur(
          reponse.status === 429
            ? "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard."
            : "Identifiant ou mot de passe incorrect."
        );
        identifiantRef.current?.focus();
        return;
      }

      const { doit_changer_mot_de_passe }: ReponseConnexionApi = await reponse.json();
      router.push(
        doit_changer_mot_de_passe
          ? "/changer-mot-de-passe"
          : safeRelativePath(searchParams.get("redirect"))
      );
    } catch {
      setErreur("Connexion au serveur impossible. Vérifiez votre réseau et réessayez.");
    } finally {
      clearTimeout(delaiAbandon);
      setEnCours(false);
    }
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
          // "off" plutot que "username" : reduit (sans l'annuler completement, certains
          // navigateurs l'ignorent sur un formulaire de connexion) le remplissage automatique
          // d'un identifiant enregistre pour cette origine. Le vrai nettoyage se fait dans le
          // gestionnaire de mots de passe du navigateur, pas dans le code.
          autoComplete="off"
          disabled={enCours}
          required
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="mot_de_passe">Mot de passe</Label>
        <InputGroup>
          <InputGroupInput
            id="mot_de_passe"
            name="mot_de_passe"
            type={motDePasseVisible ? "text" : "password"}
            autoComplete="current-password"
            disabled={enCours}
            required
          />
          <InputGroupAddon align="inline-end">
            <InputGroupButton
              type="button"
              aria-label={
                motDePasseVisible ? "Masquer le mot de passe" : "Afficher le mot de passe"
              }
              onClick={() => setMotDePasseVisible((v) => !v)}
            >
              {motDePasseVisible ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </InputGroupButton>
          </InputGroupAddon>
        </InputGroup>
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
