"use client";

import { Download, Loader2, Printer, Save } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { archiveFiche } from "@/lib/services/fiche";
import { useApiErrorToast } from "@/lib/services/error-service";
import { withMinDuration } from "@/lib/timing";

interface FicheActionsProps {
  decisionId: string;
}

export function FicheActions({ decisionId }: FicheActionsProps) {
  const [archivingInProgress, setArchivingInProgress] = useState(false);
  const [archived, setArchived] = useState(false);
  const handleError = useApiErrorToast();

  async function handleArchive() {
    setArchivingInProgress(true);
    try {
      await withMinDuration(archiveFiche(decisionId));
      toast.success("Fiche archivée.");
      setArchived(true);
    } catch (e) {
      handleError(e, "L'archivage a échoué.");
    } finally {
      setArchivingInProgress(false);
    }
  }

  return (
    <div className="flex w-[220px] flex-col gap-2">
      <Button variant="outline" className="justify-start gap-2" onClick={() => window.print()}>
        <Printer className="size-4" />
        Imprimer
      </Button>

      <Button variant="outline" className="justify-start gap-2" asChild>
        <a href={`/api/v1/scoring/${decisionId}/fiche/pdf`} download>
          <Download className="size-4" />
          Télécharger le PDF
        </a>
      </Button>

      <Button
        variant="outline"
        className="justify-start gap-2"
        onClick={handleArchive}
        loading={archivingInProgress}
        disabled={archived}
      >
        {archivingInProgress ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          <Save className="size-4" />
        )}
        {archived ? "Archivée" : "Archiver au dossier"}
      </Button>
    </div>
  );
}
