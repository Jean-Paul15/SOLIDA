"use client";

import { Download, Loader2, Printer, Save } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { archiveFiche } from "@/lib/services/fiche";
import { ApiError } from "@/lib/services/error-service";

interface FicheActionsProps {
  decisionId: string;
}

export function FicheActions({ decisionId }: FicheActionsProps) {
  const [archivageEnCours, setArchivageEnCours] = useState(false);
  const [archivee, setArchivee] = useState(false);

  async function surArchiver() {
    setArchivageEnCours(true);
    try {
      await archiveFiche(decisionId);
      toast.success("Fiche archivée.");
      setArchivee(true);
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "L'archivage a échoué.");
    } finally {
      setArchivageEnCours(false);
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
        onClick={surArchiver}
        disabled={archivageEnCours || archivee}
      >
        {archivageEnCours ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          <Save className="size-4" />
        )}
        {archivee ? "Archivée" : "Archiver au dossier"}
      </Button>
    </div>
  );
}
