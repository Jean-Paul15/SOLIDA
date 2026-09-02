"use client";

import { Eye, EyeOff } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Label } from "@/components/ui/label";
import { ApiError, useApiErrorToast } from "@/lib/services/error-service";
import { changePassword } from "@/lib/services/auth";
import { withMinDuration } from "@/lib/timing";

function PasswordField({
  id,
  label,
  autoComplete,
}: {
  id: string;
  label: string;
  autoComplete: string;
}) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <InputGroup>
        <InputGroupInput
          id={id}
          name={id}
          type={visible ? "text" : "password"}
          autoComplete={autoComplete}
          required
        />
        <InputGroupAddon align="inline-end">
          <InputGroupButton
            type="button"
            aria-label={visible ? "Masquer le mot de passe" : "Afficher le mot de passe"}
            onClick={() => setVisible((v) => !v)}
          >
            {visible ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </InputGroupButton>
        </InputGroupAddon>
      </InputGroup>
    </div>
  );
}

export function ChangePasswordForm() {
  const router = useRouter();
  const [inProgress, setInProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const handleError = useApiErrorToast();

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const formData = new FormData(event.currentTarget);
    const currentPassword = String(formData.get("mot_de_passe_actuel") ?? "");
    const newPassword = String(formData.get("nouveau_mot_de_passe") ?? "");
    const passwordConfirmation = String(formData.get("confirmation_mot_de_passe") ?? "");

    if (newPassword !== passwordConfirmation) {
      setError("Les deux mots de passe saisis ne correspondent pas.");
      return;
    }

    setInProgress(true);
    try {
      await withMinDuration(changePassword(currentPassword, newPassword));
      toast.success("Mot de passe modifié.");
      router.push("/");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Le changement a échoué.");
      handleError(e, "Le changement a échoué.");
    } finally {
      setInProgress(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex w-full flex-col gap-4">
      <PasswordField
        id="mot_de_passe_actuel"
        label="Mot de passe actuel"
        autoComplete="current-password"
      />
      <PasswordField
        id="nouveau_mot_de_passe"
        label="Nouveau mot de passe"
        autoComplete="new-password"
      />
      <PasswordField
        id="confirmation_mot_de_passe"
        label="Confirmer le nouveau mot de passe"
        autoComplete="new-password"
      />
      {error && (
        <p role="alert" className="text-sm text-decision-refus">
          {error}
        </p>
      )}
      <Button type="submit" loading={inProgress} className="w-full">
        {inProgress ? "Modification…" : "Changer le mot de passe"}
      </Button>
    </form>
  );
}
