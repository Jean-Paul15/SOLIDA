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
import { formatAmount } from "@/lib/format";
import { LABEL_TRANCHE } from "@/lib/labels";
import type { DecisionRegistreVue } from "./RegistreDecisions";

interface DecisionsTableProps {
  filtered: DecisionRegistreVue[];
}

export function DecisionsTable({ filtered }: DecisionsTableProps) {
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
          {filtered.map((d) => {
            const ecart =
              d.grantedAmount !== undefined ? d.grantedAmount - d.result.montant_recommande : null;
            return (
              <TableRow
                key={d.decisionId}
                onClick={() => router.push(`/scoring/${d.decisionId}`)}
                className="cursor-pointer"
              >
                <TableCell>
                  {new Date(d.timestamp).toLocaleString("fr-FR", {
                    dateStyle: "short",
                    timeStyle: "short",
                  })}
                </TableCell>
                <TableCell>{d.societaireNom}</TableCell>
                <TableCell>{d.agentName}</TableCell>
                <TableCell className="text-right font-mono">
                  {formatAmount(d.result.montant_demande)}
                </TableCell>
                <TableCell className="font-mono">{Math.round(d.result.score)}</TableCell>
                <TableCell>
                  <Badge variant={d.result.tranche === "refus" ? "destructive" : "secondary"}>
                    {LABEL_TRANCHE[d.result.tranche]}
                  </Badge>
                </TableCell>
                <TableCell>
                  {d.grantedAmount === undefined
                    ? "En attente"
                    : d.grantedAmount === 0
                      ? "Refusé"
                      : `Accordé ${formatAmount(d.grantedAmount)}`}
                </TableCell>
                <TableCell
                  className={
                    ecart !== null && ecart !== 0
                      ? "font-mono text-alerte"
                      : "font-mono text-neutre-500"
                  }
                >
                  {ecart === null ? "—" : ecart === 0 ? "0" : formatAmount(ecart)}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      {filtered.length === 0 && (
        <p className="py-8 text-center text-sm text-neutre-500">
          Aucune décision ne correspond à ces filtres.
        </p>
      )}
    </div>
  );
}
