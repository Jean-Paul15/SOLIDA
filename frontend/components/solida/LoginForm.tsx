"use client";

import { Eye, EyeOff, Loader2 } from "lucide-react";
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
import type { LoginResponseApi } from "@/lib/contracts";
import { safeRelativePath } from "@/lib/redirect";
import { ApiError, apiFetch } from "@/lib/services/error-service";
import { withMinDuration } from "@/lib/timing";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const identifiantRef = useRef<HTMLInputElement>(null);
  const [inProgress, setInProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordVisible, setPasswordVisible] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setInProgress(true);

    const formData = new FormData(event.currentTarget);
    // Évite un bouton bloqué si le réseau ne renvoie jamais de réponse.
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15_000);
    try {
      const response = await withMinDuration(
        apiFetch(
          "/api/v1/auth/login",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              identifiant: formData.get("identifiant"),
              mot_de_passe: formData.get("mot_de_passe"),
            }),
            signal: controller.signal,
          },
          { authRoute: true }
        )
      );

      const { must_change_password }: LoginResponseApi = await response.json();
      router.push(
        must_change_password
          ? "/changer-mot-de-passe"
          : safeRelativePath(searchParams.get("redirect"))
      );
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.message
          : "Connexion au serveur impossible. Vérifiez votre réseau et réessayez."
      );
      identifiantRef.current?.focus();
    } finally {
      clearTimeout(timeoutId);
      setInProgress(false);
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
          // Réduit l'autoremplissage d'un identifiant mémorisé pour cette origine.
          autoComplete="off"
          disabled={inProgress}
          required
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="mot_de_passe">Mot de passe</Label>
        <InputGroup>
          <InputGroupInput
            id="mot_de_passe"
            name="mot_de_passe"
            type={passwordVisible ? "text" : "password"}
            autoComplete="current-password"
            disabled={inProgress}
            required
          />
          <InputGroupAddon align="inline-end">
            <InputGroupButton
              type="button"
              aria-label={passwordVisible ? "Masquer le mot de passe" : "Afficher le mot de passe"}
              onClick={() => setPasswordVisible((v) => !v)}
            >
              {passwordVisible ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </InputGroupButton>
          </InputGroupAddon>
        </InputGroup>
      </div>
      {error && (
        <p role="alert" className="text-sm text-decision-refus">
          {error}
        </p>
      )}
      <Button type="submit" loading={inProgress} className="w-full gap-1.5">
        {inProgress && <Loader2 className="size-4 animate-spin" />}
        {inProgress ? "Connexion…" : "Se connecter"}
      </Button>
    </form>
  );
}
