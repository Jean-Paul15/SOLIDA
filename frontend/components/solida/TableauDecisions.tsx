"use client";

import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formaterMontant } from "@/lib/format";
import { LIBELLE_TRANCHE } from "@/lib/libelles";
import type { DecisionRegistreVue } from "./RegistreDecisions";

interface TableauDecisionsProps {
  filtrees: DecisionRegistreVue[];
}

export function TableauDecisions({ filtrees }: TableauDecisionsProps) {
  const router = useRouter();

  return (
    <div className="flex flex-col gap-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date et heure</TableHead>
            <TableHead>Sociétaire</TableHead>
            <TableHead>Agent</TableHead>
            <TableHead>Montant sollicité</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Tranche</TableHead>
            <TableHead>Décision finale</TableHead>
            <TableHead>Écart</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtrees.map((d) => {
            const ecart =
              d.montantAccorde !== undefined
                ? d.montantAccorde - d.resultat.montant_recommande
                : null;
            return (
              <TableRow
                key={d.decisionId}
                onClick={() => router.push(`/scoring/${d.decisionId}`)}
                className="cursor-pointer"
              >
                <TableCell>
                  {new Date(d.horodatage).toLocaleString("fr-FR", {
                    dateStyle: "short",
                    timeStyle: "short",
                  })}
                </TableCell>
                <TableCell>{d.societaireNom}</TableCell>
                <TableCell>{d.agentNom}</TableCell>
                <TableCell className="text-right font-mono">
                  {formaterMontant(d.resultat.montant_demande)}
                </TableCell>
                <TableCell className="font-mono">{Math.round(d.resultat.score)}</TableCell>
                <TableCell>
                  <Badge variant={d.resultat.tranche === "refus" ? "destructive" : "secondary"}>
                    {LIBELLE_TRANCHE[d.resultat.tranche]}
                  </Badge>
                </TableCell>
                <TableCell>
                  {d.montantAccorde === undefined
                    ? "En attente"
                    : d.montantAccorde === 0
                      ? "Refusé"
                      : `Accordé ${formaterMontant(d.montantAccorde)}`}
                </TableCell>
                <TableCell
                  className={
                    ecart !== null && ecart !== 0
                      ? "font-mono text-alerte"
                      : "font-mono text-neutre-500"
                  }
                >
                  {ecart === null ? "—" : ecart === 0 ? "0" : formaterMontant(ecart)}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      {filtrees.length === 0 && (
        <p className="py-8 text-center text-sm text-neutre-500">
          Aucune décision ne correspond à ces filtres.
        </p>
      )}
    </div>
  );
}
