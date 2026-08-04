"use client";

import { Download, Printer, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export function FicheActions() {
  return (
    <div className="flex w-[220px] flex-col gap-2">
      <Button variant="outline" className="justify-start gap-2" onClick={() => window.print()}>
        <Printer className="size-4" />
        Imprimer
      </Button>

      <Tooltip>
        <TooltipTrigger asChild>
          <span>
            <Button variant="outline" className="w-full justify-start gap-2" disabled>
              <Download className="size-4" />
              Télécharger le PDF
            </Button>
          </span>
        </TooltipTrigger>
        <TooltipContent>
          Génération PDF côté serveur (WeasyPrint) — nécessite le backend, pas encore construit.
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <span>
            <Button variant="outline" className="w-full justify-start gap-2" disabled>
              <Save className="size-4" />
              Archiver au dossier
            </Button>
          </span>
        </TooltipTrigger>
        <TooltipContent>
          Archivage MinIO et journal d&rsquo;audit — nécessite le backend, pas encore construit.
        </TooltipContent>
      </Tooltip>
    </div>
  );
}
