"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ResultatScoring } from "@/lib/contracts";
import { formaterMontant } from "@/lib/format";
import { LIBELLE_TRANCHE } from "@/lib/libelles";

export interface DecisionRegistreVue {
  decisionId: string;
  societaireId: string;
  societaireNom: string;
  agence: string;
  resultat: ResultatScoring;
  horodatage: string;
  agentNom: string;
  /** Toujours `undefined` : la finalisation d'une décision (montant réellement accordé)
   * n'est pas encore modélisée côté backend (`decision_finale`, voir
   * docs/backend/02-persistance-et-migrations.md). */
  montantAccorde?: number;
}

const PERIODES = [
  { valeur: "7", libelle: "7 derniers jours" },
  { valeur: "30", libelle: "30 derniers jours" },
  { valeur: "90", libelle: "90 derniers jours" },
  { valeur: "tout", libelle: "Toute la période" },
];

const TOUS = "__tous__";

interface RegistreDecisionsProps {
  decisions: DecisionRegistreVue[];
}

export function RegistreDecisions({ decisions }: RegistreDecisionsProps) {
  const router = useRouter();
  const [maintenant] = useState(() => Date.now());
  const [periode, setPeriode] = useState("30");
  const [agence, setAgence] = useState(TOUS);
  const [agent, setAgent] = useState(TOUS);
  const [tranche, setTranche] = useState(TOUS);

  const agences = useMemo(() => [...new Set(decisions.map((d) => d.agence))].sort(), [decisions]);
  const agents = useMemo(() => [...new Set(decisions.map((d) => d.agentNom))].sort(), [decisions]);

  const filtrees = useMemo(() => {
    const seuil = periode === "tout" ? null : maintenant - Number(periode) * 24 * 60 * 60 * 1000;
    return decisions.filter((d) => {
      if (seuil !== null && new Date(d.horodatage).getTime() < seuil) return false;
      if (agence !== TOUS && d.agence !== agence) return false;
      if (agent !== TOUS && d.agentNom !== agent) return false;
      if (tranche !== TOUS && d.resultat.tranche !== tranche) return false;
      return true;
    });
  }, [decisions, periode, agence, agent, tranche, maintenant]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-3">
        <Select value={periode} onValueChange={setPeriode}>
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PERIODES.map((p) => (
              <SelectItem key={p.valeur} value={p.valeur}>
                {p.libelle}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={agence} onValueChange={setAgence}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Toutes les agences" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={TOUS}>Toutes les agences</SelectItem>
            {agences.map((a) => (
              <SelectItem key={a} value={a}>
                {a}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={agent} onValueChange={setAgent}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Tous les agents" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={TOUS}>Tous les agents</SelectItem>
            {agents.map((a) => (
              <SelectItem key={a} value={a}>
                {a}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={tranche} onValueChange={setTranche}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Toutes les tranches" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={TOUS}>Toutes les tranches</SelectItem>
            {Object.entries(LIBELLE_TRANCHE).map(([valeur, libelle]) => (
              <SelectItem key={valeur} value={valeur}>
                {libelle}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

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
