"use client";

import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { SyntheseGroupe } from "@/lib/contracts";
import { LABEL_STATUT_CREDIT_MEMBRE } from "@/lib/labels";
import { ApiError, useApiErrorToast } from "@/lib/services/error-service";
import { fetchGroup } from "@/lib/services/societaires";

const LABEL_ROLE: Record<string, string> = {
  membre: "Membre",
  presidente: "Présidente",
  tresoriere: "Trésorière",
  secretaire: "Secrétaire",
};

interface GroupeCautionDialogProps {
  societaireId: string;
}

export function GroupeCautionDialog({ societaireId }: GroupeCautionDialogProps) {
  const router = useRouter();
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

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Membre</TableHead>
                  <TableHead>Rôle</TableHead>
                  <TableHead>Ancienneté</TableHead>
                  <TableHead>Statut crédit</TableHead>
                  <TableHead>Caution appelée</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {groupe.membres.map((m) => (
                  <TableRow
                    key={m.societaire_id}
                    onClick={() => router.push(`/societaires/${m.societaire_id}`)}
                    className={
                      m.societaire_id === societaireId
                        ? "cursor-pointer bg-solida-teal-50"
                        : "cursor-pointer"
                    }
                  >
                    <TableCell>{m.nom_complet}</TableCell>
                    <TableCell>{LABEL_ROLE[m.role]}</TableCell>
                    <TableCell>{Math.floor(m.anciennete_mois / 12)} an(s)</TableCell>
                    <TableCell>
                      <Badge
                        variant={m.statut_credit === "en_souffrance" ? "destructive" : "secondary"}
                      >
                        {LABEL_STATUT_CREDIT_MEMBRE[m.statut_credit]}
                      </Badge>
                    </TableCell>
                    <TableCell>{m.caution_appelee ? "Oui" : "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

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
