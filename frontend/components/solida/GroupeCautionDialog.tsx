"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import type { SyntheseGroupe } from "@/lib/contracts";
import { ApiError, useApiErrorToast } from "@/lib/services/error-service";
import { fetchGroup } from "@/lib/services/societaires";
import { GroupMembersTable } from "./GroupMembersTable";

interface GroupeCautionDialogProps {
  societaireId: string;
}

export function GroupeCautionDialog({ societaireId }: GroupeCautionDialogProps) {
  const handleError = useApiErrorToast();
  const [groupe, setGroupe] = useState<SyntheseGroupe | null>(null);
  const [inProgress, setInProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setInProgress(true);
    setError(null);
    fetchGroup(societaireId)
      .then(setGroupe)
      .catch((e: unknown) => {
        setError(
          e instanceof ApiError ? e.message : "Le groupe de caution n'a pas pu être chargé."
        );
        if (e instanceof ApiError && e.kind === "session_expired") {
          handleError(e, "");
        }
      })
      .finally(() => setInProgress(false));
  }

  function handleOpenChange(open: boolean) {
    if (!open || groupe || inProgress) return;
    load();
  }

  return (
    <Dialog onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Voir le groupe
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[560px] gap-4 overflow-y-auto sm:max-w-[720px]">
        {inProgress && (
          <div className="flex flex-1 items-center justify-center gap-2 py-10 text-sm text-neutre-500">
            <Loader2 className="size-4 animate-spin" />
            Chargement du groupe…
          </div>
        )}

        {error && (
          <div className="flex flex-col items-center gap-2 py-10 text-center text-sm text-decision-refus">
            <p>{error}</p>
            <button
              type="button"
              onClick={load}
              className="cursor-pointer text-solida-teal-800 underline"
            >
              Réessayer
            </button>
          </div>
        )}

        {groupe && (
          <>
            <DialogHeader>
              <DialogTitle>{groupe.nom_groupe}</DialogTitle>
              <DialogDescription>
                Créé le{" "}
                {new Date(groupe.date_creation).toLocaleDateString("fr-FR", {
                  month: "long",
                  year: "numeric",
                })}{" "}
                · {groupe.taille_actuelle} membres
              </DialogDescription>
            </DialogHeader>

            <div className="flex items-center gap-2">
              <span className="text-sm text-neutre-500">Taux de remboursement collectif</span>
              <span className="font-mono text-lg text-neutre-950">
                {groupe.taux_remboursement_groupe !== null
                  ? `${Math.round(groupe.taux_remboursement_groupe * 100)}%`
                  : "—"}
              </span>
            </div>

            <GroupMembersTable members={groupe.membres} societaireId={societaireId} />

            <div className="flex justify-between border-t border-neutre-200 pt-3 text-sm text-neutre-500">
              <span>{groupe.nb_cycles_completes} cycle(s) menés à terme</span>
              <span>{groupe.nb_sorties_12m} sortie(s) sur 12 mois</span>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
